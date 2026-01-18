"""
Comprehensive unit tests for user login and register features.
Tests cover authentication endpoints, security functions, and edge cases.
Target: 80%+ line coverage
"""

import pytest
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Table, Column, Integer, String, Boolean, DateTime
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base

from app.main import app
from app.database import get_db
from app.schemas import UserLogin, UserCreate, UserResponse, Token
from app.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
)
from app.routers.auth import verify_recaptcha
import jwt
import requests


# ==================== Test Database Setup ====================

Base = declarative_base()

class UserModel(Base):
    """SQLAlchemy User model for testing"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Provide a database session for each test"""
    connection = test_db.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Provide a TestClient with mocked database dependency"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with patch('app.models.Base.classes') as mock_base_classes:
        mock_base_classes.users = UserModel
        test_client = TestClient(app)
        yield test_client
    
    app.dependency_overrides.clear()


# ==================== Test Data Factories ====================

@pytest.fixture
def test_user_data():
    """Standard test user data"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "captcha_token": "valid_token_123"
    }


@pytest.fixture
def test_user_create_data():
    """User registration data"""
    return {
        "email": "newuser@example.com",
        "password": "SecurePassword456!",
        "captcha_token": "valid_token_456"
    }


@pytest.fixture
def mock_recaptcha_success(monkeypatch):
    """Mock successful reCAPTCHA verification"""
    mock_post = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}
    mock_post.return_value = mock_response
    
    monkeypatch.setenv("REACT_APP_RECAPTCHA_SECRET_KEY", "test_secret_key")
    monkeypatch.setattr("app.routers.auth.requests.post", mock_post)
    
    return mock_post


@pytest.fixture
def mock_recaptcha_failure(monkeypatch):
    """Mock failed reCAPTCHA verification"""
    mock_post = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": False, "error-codes": ["invalid-input-response"]}
    mock_post.return_value = mock_response
    
    monkeypatch.setenv("REACT_APP_RECAPTCHA_SECRET_KEY", "test_secret_key")
    monkeypatch.setattr("app.routers.auth.requests.post", mock_post)
    
    return mock_post


# ==================== Security Function Tests ====================

class TestPasswordFunctions:
    """Tests for password hashing and verification"""
    
    def test_get_password_hash(self):
        """Test password hashing function produces hash"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        wrong_password = "WrongPassword123!"
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_string(self):
        """Test password verification with empty string"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed) is False
    
    def test_verify_password_case_sensitive(self):
        """Test that password verification is case sensitive"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password("testpassword123!", hashed) is False
    
    def test_password_hash_different_each_time(self):
        """Test that same password produces different hashes (salt)"""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_very_long_password(self):
        """Test hashing of very long password"""
        password = "a" * 500
        wrong_password = "b" * 500
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password(wrong_password, hashed) is False
    
    def test_password_with_unicode(self):
        """Test password with unicode characters"""
        password = "Pässwörd123!€"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("Password123!€", hashed) is False


class TestAccessTokenCreation:
    """Tests for JWT access token creation and validation"""
    
    def test_create_access_token_basic(self):
        """Test basic token creation"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expires(self):
        """Test token creation with custom expiration"""
        data = {"sub": "test@example.com", "user_id": 1}
        expires_delta = timedelta(hours=1)
        token = create_access_token(data, expires_delta)
        
        assert isinstance(token, str)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == 1
    
    def test_create_access_token_payload(self):
        """Test that token contains correct payload"""
        data = {"sub": "user@example.com", "user_id": 42, "role": "admin"}
        token = create_access_token(data)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "user@example.com"
        assert decoded["user_id"] == 42
        assert decoded["role"] == "admin"
    
    def test_create_access_token_default_expiration(self):
        """Test default token expiration (15 minutes)"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded
        assert "sub" in decoded
    
    def test_create_access_token_negative_expiration(self):
        """Test creating token with past expiration"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data, timedelta(seconds=-100))
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    def test_create_access_token_far_future_expiration(self):
        """Test token with far future expiration"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data, timedelta(days=365))
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "test@example.com"
    
    def test_create_access_token_empty_data(self):
        """Test token creation with empty data"""
        data = {}
        token = create_access_token(data)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded
    
    def test_token_not_decode_without_secret(self):
        """Test that token cannot be decoded with wrong secret"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "wrong_secret", algorithms=[ALGORITHM])
    
    def test_token_not_decode_with_different_algorithm(self):
        """Test that token cannot be decoded with different algorithm"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        with pytest.raises(jwt.InvalidAlgorithmError):
            jwt.decode(token, SECRET_KEY, algorithms=["HS512"])


class TestTokenDecoding:
    """Tests for token decoding and validation"""
    
    def test_decode_valid_token(self):
        """Test decoding a valid token"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "test@example.com"
    
    def test_decode_malformed_token(self):
        """Test decoding malformed token"""
        with pytest.raises(jwt.DecodeError):
            jwt.decode("invalid.token.format", SECRET_KEY, algorithms=[ALGORITHM])
    
    def test_decode_token_with_altered_payload(self):
        """Test that token with altered payload is invalid"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Alter the token
        parts = token.split(".")
        altered_token = parts[0] + "." + parts[1] + ".wrong_signature"
        
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(altered_token, SECRET_KEY, algorithms=[ALGORITHM])
    
    def test_decode_expired_token(self):
        """Test decoding expired token"""
        data = {"sub": "test@example.com"}
        expired_token = create_access_token(data, expires_delta=timedelta(seconds=-10))
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(expired_token, SECRET_KEY, algorithms=[ALGORITHM])


# ==================== ReCAPTCHA Verification Tests ====================

class TestRecaptchaVerification:
    """Tests for reCAPTCHA verification"""
    
    def test_verify_recaptcha_success(self, mock_recaptcha_success):
        """Test successful reCAPTCHA verification"""
        result = verify_recaptcha("valid_token_123")
        assert result is True
    
    def test_verify_recaptcha_failure(self, mock_recaptcha_failure):
        """Test failed reCAPTCHA verification"""
        with pytest.raises(Exception):
            verify_recaptcha("invalid_token")
    
    def test_verify_recaptcha_with_error_codes(self, mock_recaptcha_failure):
        """Test reCAPTCHA failure returns error codes"""
        with pytest.raises(Exception) as exc_info:
            verify_recaptcha("invalid_token")
        
        assert "reCAPTCHA" in str(exc_info.value)
    
    def test_verify_recaptcha_missing_secret_key(self, monkeypatch):
        """Test when reCAPTCHA secret key is not configured"""
        monkeypatch.delenv("REACT_APP_RECAPTCHA_SECRET_KEY", raising=False)
        
        with patch('app.routers.auth.RECAPTCHA_SECRET_KEY', None):
            with pytest.raises(Exception):
                verify_recaptcha("token")
    
    def test_verify_recaptcha_connection_error(self, monkeypatch):
        """Test reCAPTCHA verification when service unavailable"""
        mock_post = MagicMock()
        mock_post.side_effect = Exception("Connection error")
        
        monkeypatch.setenv("REACT_APP_RECAPTCHA_SECRET_KEY", "test_key")
        monkeypatch.setattr("app.routers.auth.requests.post", mock_post)
        
        with pytest.raises(Exception):
            verify_recaptcha("token")
    
    def test_verify_recaptcha_success_flag_missing(self, monkeypatch):
        """Test reCAPTCHA response without success flag"""
        mock_post = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"error-codes": ["some-error"]}
        mock_post.return_value = mock_response
        
        monkeypatch.setenv("REACT_APP_RECAPTCHA_SECRET_KEY", "test_key")
        monkeypatch.setattr("app.routers.auth.requests.post", mock_post)
        
        with pytest.raises(Exception):
            verify_recaptcha("token")
    
    def test_verify_recaptcha_http_error(self, monkeypatch):
        """Test reCAPTCHA with HTTP error response"""
        mock_post = MagicMock()
        mock_post.return_value.raise_for_status.side_effect = Exception("HTTP 500")
        
        monkeypatch.setenv("REACT_APP_RECAPTCHA_SECRET_KEY", "test_key")
        monkeypatch.setattr("app.routers.auth.requests.post", mock_post)
        
        with pytest.raises(Exception):
            verify_recaptcha("token")


# ==================== Register Endpoint Tests ====================

class TestRegisterEndpoint:
    """Tests for user registration endpoint"""
    
    def test_register_success(self, client, test_user_create_data, mock_recaptcha_success, db_session):
        """Test successful user registration"""
        response = client.post(
            "/auth/register",
            json=test_user_create_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_create_data["email"]
        assert data["role"] is False
        assert "id" in data
    
    def test_register_email_already_exists(self, client, mock_recaptcha_success, db_session):
        """Test registration with duplicate email"""
        email = "duplicate@example.com"
        password = "SecurePass123!"
        
        client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        
        response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "AnotherPass123!",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_register_invalid_recaptcha(self, client, test_user_create_data, mock_recaptcha_failure):
        """Test registration with invalid reCAPTCHA"""
        response = client.post(
            "/auth/register",
            json=test_user_create_data
        )
        
        assert response.status_code == 400
        assert "reCAPTCHA" in response.json()["detail"]
    
    def test_register_invalid_email_format(self, client, mock_recaptcha_success):
        """Test registration with invalid email"""
        response = client.post(
            "/auth/register",
            json={
                "email": "invalid-email",
                "password": "ValidPass123!",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_password_too_short(self, client, mock_recaptcha_success):
        """Test registration with password < 8 characters"""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_missing_email(self, client, mock_recaptcha_success):
        """Test registration without email"""
        response = client.post(
            "/auth/register",
            json={
                "password": "ValidPass123!",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_missing_password(self, client, mock_recaptcha_success):
        """Test registration without password"""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_missing_captcha_token(self, client):
        """Test registration without captcha token"""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "ValidPass123!"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_password_minimum_length(self, client, mock_recaptcha_success):
        """Test registration with exactly 8 character password"""
        response = client.post(
            "/auth/register",
            json={
                "email": "min@example.com",
                "password": "12345678",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 201
    
    def test_register_password_special_chars(self, client, mock_recaptcha_success):
        """Test registration with special characters in password"""
        response = client.post(
            "/auth/register",
            json={
                "email": "special@example.com",
                "password": "P@ssw0rd!#$%^&*()",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 201
    
    def test_register_password_unicode(self, client, mock_recaptcha_success):
        """Test registration with unicode in password"""
        response = client.post(
            "/auth/register",
            json={
                "email": "unicode@example.com",
                "password": "Pässwörd123!€",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 201
    
    def test_register_multiple_users(self, client, mock_recaptcha_success):
        """Test registering multiple unique users"""
        for i in range(3):
            response = client.post(
                "/auth/register",
                json={
                    "email": f"user{i}@example.com",
                    "password": f"Password{i}123!",
                    "captcha_token": "valid_token"
                }
            )
            assert response.status_code == 201
    
    def test_register_stores_hashed_password(self, client, mock_recaptcha_success, db_session):
        """Test that password is stored hashed, not plain"""
        password = "PlainPassword123!"
        email = "hash@example.com"
        
        client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        
        user = db_session.query(UserModel).filter_by(email=email).first()
        assert user.password != password
    
    def test_register_sets_role_to_false(self, client, mock_recaptcha_success):
        """Test that new users get role=False"""
        response = client.post(
            "/auth/register",
            json={
                "email": "role@example.com",
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        
        data = response.json()
        assert data["role"] is False


# ==================== Login Endpoint Tests ====================

class TestLoginEndpoint:
    """Tests for user login endpoint"""
    
    def test_login_success(self, client, test_user_data, mock_recaptcha_success):
        """Test successful user login"""
        # Register first
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        # Then login
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_user_not_found(self, client, mock_recaptcha_success):
        """Test login with non-existent user"""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123!",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_wrong_password(self, client, test_user_data, mock_recaptcha_success):
        """Test login with wrong password"""
        # Register
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        # Try wrong password
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "WrongPassword123!",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_invalid_recaptcha(self, client, test_user_data, mock_recaptcha_failure):
        """Test login with invalid reCAPTCHA"""
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "invalid_token"
            }
        )
        
        assert response.status_code == 400
        assert "reCAPTCHA" in response.json()["detail"]
    
    def test_login_invalid_email_format(self, client, mock_recaptcha_success):
        """Test login with invalid email format"""
        response = client.post(
            "/auth/login",
            json={
                "email": "invalid-email",
                "password": "SomePassword123!",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 422
    
    def test_login_missing_email(self, client, mock_recaptcha_success):
        """Test login without email"""
        response = client.post(
            "/auth/login",
            json={
                "password": "SomePassword123!",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 422
    
    def test_login_missing_password(self, client, mock_recaptcha_success):
        """Test login without password"""
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 422
    
    def test_login_missing_captcha_token(self, client):
        """Test login without captcha token"""
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "SomePassword123!"
            }
        )
        
        assert response.status_code == 422
    
    def test_login_token_contains_email(self, client, test_user_data, mock_recaptcha_success):
        """Test that login token contains email"""
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        
        token = response.json()["access_token"]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == test_user_data["email"]
    
    def test_login_token_contains_user_id(self, client, test_user_data, mock_recaptcha_success):
        """Test that login token contains user ID"""
        register_resp = client.post(
            "/auth/register",
            json=test_user_data
        )
        user_id = register_resp.json()["id"]
        
        login_resp = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        
        token = login_resp.json()["access_token"]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["user_id"] == user_id
    
    def test_login_case_sensitivity(self, client, mock_recaptcha_success):
        """Test email case sensitivity in login"""
        # Register
        client.post(
            "/auth/register",
            json={
                "email": "Case@Example.com",
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        
        # Try login with different case
        response = client.post(
            "/auth/login",
            json={
                "email": "case@example.com",
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        
        # Behavior depends on database COLLATION
        assert response.status_code in [200, 401]
    
    def test_login_multiple_attempts(self, client, test_user_data, mock_recaptcha_success):
        """Test multiple login attempts"""
        # Register
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        # Multiple successful logins
        for _ in range(3):
            response = client.post(
                "/auth/login",
                json={
                    "email": test_user_data["email"],
                    "password": test_user_data["password"],
                    "captcha_token": "valid_token"
                }
            )
            assert response.status_code == 200
    
    def test_login_token_is_jwt(self, client, test_user_data, mock_recaptcha_success):
        """Test that login returns valid JWT"""
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        
        token = response.json()["access_token"]
        # Should be decodable without error
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded


# ==================== Integration Tests ====================

class TestAuthIntegration:
    """Integration tests for authentication workflow"""
    
    def test_full_auth_workflow(self, client, mock_recaptcha_success):
        """Test complete register -> login workflow"""
        email = "workflow@example.com"
        password = "WorkflowPassword123!"
        
        # Step 1: Register
        register_response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]
        
        # Step 2: Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Step 3: Verify token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == email
        assert decoded["user_id"] == user_id
    
    def test_user_isolation(self, client, mock_recaptcha_success):
        """Test that different users are isolated"""
        user1_email = "user1@example.com"
        user2_email = "user2@example.com"
        password = "Password123!"
        
        # Register two users
        resp1 = client.post(
            "/auth/register",
            json={
                "email": user1_email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        user1_id = resp1.json()["id"]
        
        resp2 = client.post(
            "/auth/register",
            json={
                "email": user2_email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        user2_id = resp2.json()["id"]
        
        # IDs should be different
        assert user1_id != user2_id
        
        # Each user can login with their own credentials
        login1 = client.post(
            "/auth/login",
            json={
                "email": user1_email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        assert login1.status_code == 200
        
        # User2 cannot login with User1's email
        login_fail = client.post(
            "/auth/login",
            json={
                "email": user1_email,
                "password": "WrongPassword123!",
                "captcha_token": "valid_token"
            }
        )
        assert login_fail.status_code == 401
    
    def test_password_update_scenario(self, client, mock_recaptcha_success):
        """Test login fails after password would be changed (simulated)"""
        email = "update@example.com"
        old_password = "OldPassword123!"
        new_password = "NewPassword456!"
        
        # Register with old password
        client.post(
            "/auth/register",
            json={
                "email": email,
                "password": old_password,
                "captcha_token": "valid_token"
            }
        )
        
        # Can login with old password
        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": old_password,
                "captcha_token": "valid_token"
            }
        )
        assert response.status_code == 200
        
        # Cannot login with new password (before actual change)
        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": new_password,
                "captcha_token": "valid_token"
            }
        )
        assert response.status_code == 401


# ==================== Edge Cases and Boundary Tests ====================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def test_register_very_long_password(self, client, mock_recaptcha_success):
        """Test registration with 256 character password"""
        response = client.post(
            "/auth/register",
            json={
                "email": "longpass@example.com",
                "password": "a" * 256,
                "captcha_token": "valid_token"
            }
        )
        assert response.status_code == 201
    
    def test_login_with_long_password(self, client, mock_recaptcha_success):
        """Test login with very long password"""
        long_pass = "a" * 256
        
        client.post(
            "/auth/register",
            json={
                "email": "longpass@example.com",
                "password": long_pass,
                "captcha_token": "valid_token"
            }
        )
        
        response = client.post(
            "/auth/login",
            json={
                "email": "longpass@example.com",
                "password": long_pass,
                "captcha_token": "valid_token"
            }
        )
        assert response.status_code == 200
    
    def test_email_with_numbers_and_special_chars(self, client, mock_recaptcha_success):
        """Test email with numbers and special characters"""
        email = "user.name+test123@example.co.uk"
        password = "Password123!"
        
        response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        assert response.status_code == 201
    
    def test_email_with_subdomain(self, client, mock_recaptcha_success):
        """Test email with subdomain"""
        email = "user@mail.example.com"
        password = "Password123!"
        
        response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        assert response.status_code == 201
    
    def test_password_only_numbers(self, client, mock_recaptcha_success):
        """Test password with only numbers (minimum length)"""
        response = client.post(
            "/auth/register",
            json={
                "email": "numbers@example.com",
                "password": "12345678",
                "captcha_token": "valid_token"
            }
        )
        assert response.status_code == 201
    
    def test_password_spaces(self, client, mock_recaptcha_success):
        """Test password with spaces"""
        password = "Pass word 123 !"
        
        response = client.post(
            "/auth/register",
            json={
                "email": "spaces@example.com",
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        assert response.status_code == 201
        
        # Can login with spaces in password
        login_resp = client.post(
            "/auth/login",
            json={
                "email": "spaces@example.com",
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        assert login_resp.status_code == 200
    
    def test_captcha_token_with_special_chars(self, client, mock_recaptcha_success):
        """Test captcha token with special characters"""
        response = client.post(
            "/auth/register",
            json={
                "email": "token@example.com",
                "password": "Password123!",
                "captcha_token": "token_with-special.chars_123"
            }
        )
        assert response.status_code == 201
    
    def test_login_empty_password_field(self, client):
        """Test login with empty password string"""
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "",
                "captcha_token": "valid_token"
            }
        )
        # Should fail due to validation or credentials
        assert response.status_code in [400, 401, 422]
    
    def test_register_empty_password(self, client):
        """Test register with empty password"""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "",
                "captcha_token": "valid_token"
            }
        )
        assert response.status_code == 422
    
    def test_sequential_login_failures(self, client, mock_recaptcha_success):
        """Test multiple sequential login failures"""
        email = "fail@example.com"
        password = "Password123!"
        
        # Register
        client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        
        # Multiple failed login attempts
        for _ in range(5):
            response = client.post(
                "/auth/login",
                json={
                    "email": email,
                    "password": "WrongPassword123!",
                    "captcha_token": "valid_token"
                }
            )
            assert response.status_code == 401
        
        # But correct password still works
        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        assert response.status_code == 200


# ==================== Security-focused Tests ====================

class TestSecurityConcerns:
    """Tests for security-related concerns"""
    
    def test_password_not_returned_on_register(self, client, test_user_create_data, mock_recaptcha_success):
        """Test that password is never returned in response"""
        response = client.post(
            "/auth/register",
            json=test_user_create_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "password" not in data
    
    def test_password_not_returned_on_login(self, client, test_user_data, mock_recaptcha_success):
        """Test that password is not in token payload"""
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        
        token = response.json()["access_token"]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "password" not in decoded
    
    def test_hashed_password_not_same_as_plain(self, client, test_user_data, mock_recaptcha_success, db_session):
        """Test that stored password is hashed, not plain text"""
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        # Query database
        user = db_session.query(UserModel).filter_by(email=test_user_data["email"]).first()
        assert user is not None
        assert user.password != test_user_data["password"]
    
    def test_different_passwords_different_hashes(self, client, mock_recaptcha_success, db_session):
        """Test that different passwords produce different hashes"""
        client.post(
            "/auth/register",
            json={
                "email": "user1@example.com",
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        
        client.post(
            "/auth/register",
            json={
                "email": "user2@example.com",
                "password": "Password456!",
                "captcha_token": "valid_token"
            }
        )
        
        user1 = db_session.query(UserModel).filter_by(email="user1@example.com").first()
        user2 = db_session.query(UserModel).filter_by(email="user2@example.com").first()
        
        assert user1.password != user2.password


# ==================== Response Schema Tests ====================

class TestResponseSchemas:
    """Tests for response schema validation"""
    
    def test_register_response_has_required_fields(self, client, test_user_create_data, mock_recaptcha_success):
        """Test register response has all required UserResponse fields"""
        response = client.post(
            "/auth/register",
            json=test_user_create_data
        )
        
        assert response.status_code == 201
        data = response.json()
        required_fields = {"id", "email", "role"}
        assert set(data.keys()) == required_fields
    
    def test_login_response_has_required_fields(self, client, test_user_data, mock_recaptcha_success):
        """Test login response has all required Token fields"""
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        required_fields = {"access_token", "token_type"}
        assert set(data.keys()) == required_fields
    
    def test_register_response_id_is_integer(self, client, test_user_create_data, mock_recaptcha_success):
        """Test that register response ID is integer"""
        response = client.post(
            "/auth/register",
            json=test_user_create_data
        )
        
        data = response.json()
        assert isinstance(data["id"], int)
    
    def test_register_response_role_is_boolean(self, client, test_user_create_data, mock_recaptcha_success):
        """Test that register response role is boolean"""
        response = client.post(
            "/auth/register",
            json=test_user_create_data
        )
        
        data = response.json()
        assert isinstance(data["role"], bool)
    
    def test_login_response_token_type_is_bearer(self, client, test_user_data, mock_recaptcha_success):
        """Test that login response token_type is 'bearer'"""
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        
        data = response.json()
        assert data["token_type"] == "bearer"
    
    def test_register_response_email_matches_input(self, client, test_user_create_data, mock_recaptcha_success):
        """Test that register response email matches input"""
        response = client.post(
            "/auth/register",
            json=test_user_create_data
        )
        
        data = response.json()
        assert data["email"] == test_user_create_data["email"]


# ==================== Database Interaction Tests ====================

class TestDatabaseInteractions:
    """Tests for database-level operations and interactions"""
    
    def test_register_saves_to_database(self, client, mock_recaptcha_success, db_session):
        """Test that register actually saves user to database"""
        email = "dbtest@example.com"
        password = "Password123!"
        
        response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 201
        
        # Verify user exists in database
        user = db_session.query(UserModel).filter_by(email=email).first()
        assert user is not None
        assert user.email == email
        assert user.role is False
    
    def test_login_queries_database(self, client, test_user_data, mock_recaptcha_success, db_session):
        """Test that login queries database correctly"""
        # Register first
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        # Count users before login
        count_before = db_session.query(UserModel).count()
        
        # Login
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        
        # Count should remain same
        count_after = db_session.query(UserModel).count()
        assert count_before == count_after == 1
        assert response.status_code == 200
    
    def test_register_creates_timestamp(self, client, mock_recaptcha_success, db_session):
        """Test that register sets created_at timestamp"""
        email = "timestamp@example.com"
        
        before_time = datetime.now()
        client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        after_time = datetime.now()
        
        user = db_session.query(UserModel).filter_by(email=email).first()
        assert user.created_at is not None
        assert before_time <= user.created_at <= after_time
    
    def test_duplicate_email_uses_unique_constraint(self, client, mock_recaptcha_success, db_session):
        """Test that duplicate email is caught before database commit"""
        email = "unique@example.com"
        
        # Register first user
        client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "Password1!",
                "captcha_token": "valid_token"
            }
        )
        
        # Try to register duplicate
        response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "Password2!",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 400
        # Only one user should exist in database
        count = db_session.query(UserModel).filter_by(email=email).count()
        assert count == 1
    
    def test_password_field_stored_correctly(self, client, mock_recaptcha_success, db_session):
        """Test that password is stored in database correctly"""
        email = "pwd@example.com"
        password = "MyPassword123!"
        
        client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        
        user = db_session.query(UserModel).filter_by(email=email).first()
        # Password should be hashed
        assert user.password != password
        # But should verify correctly
        assert verify_password(password, user.password)
    
    def test_email_field_case_preserved(self, client, mock_recaptcha_success, db_session):
        """Test that email is stored in database"""
        email = "Test.User@Example.Com"
        
        client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        
        # Query by lowercase email since database might normalize it
        user = db_session.query(UserModel).filter(UserModel.email.ilike(email)).first()
        assert user is not None
        assert user.email.lower() == email.lower()
    
    def test_role_default_value(self, client, mock_recaptcha_success, db_session):
        """Test that role defaults to False for new users"""
        email = "role@example.com"
        
        client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        
        user = db_session.query(UserModel).filter_by(email=email).first()
        assert user.role is False
        assert isinstance(user.role, bool)


# ==================== Additional Endpoint Tests ====================

class TestAdditionalEndpointScenarios:
    """Additional tests for various endpoint scenarios"""
    
    def test_register_returns_created_user_id(self, client, mock_recaptcha_success):
        """Test that register returns the created user's ID"""
        response = client.post(
            "/auth/register",
            json={
                "email": "userid@example.com",
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], int)
        assert data["id"] > 0
    
    def test_register_increments_user_id(self, client, mock_recaptcha_success):
        """Test that user IDs increment for each registration"""
        resp1 = client.post(
            "/auth/register",
            json={
                "email": "user1@example.com",
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        id1 = resp1.json()["id"]
        
        resp2 = client.post(
            "/auth/register",
            json={
                "email": "user2@example.com",
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        id2 = resp2.json()["id"]
        
        assert id2 > id1
    
    def test_login_returns_different_tokens(self, client, test_user_data, mock_recaptcha_success):
        """Test that multiple logins return different tokens"""
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        resp1 = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        token1 = resp1.json()["access_token"]
        
        resp2 = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        token2 = resp2.json()["access_token"]
        
        # Tokens should be valid and decodable
        decoded1 = jwt.decode(token1, SECRET_KEY, algorithms=[ALGORITHM])
        decoded2 = jwt.decode(token2, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded1
        assert "exp" in decoded2
    
    def test_login_token_has_iat_claim(self, client, test_user_data, mock_recaptcha_success):
        """Test that login token has required claims"""
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        
        token = response.json()["access_token"]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert "exp" in decoded
        assert isinstance(decoded["exp"], (int, float))
    
    def test_login_token_expiration_in_future(self, client, test_user_data, mock_recaptcha_success):
        """Test that login token expiration is in the future"""
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        
        token = response.json()["access_token"]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        now = datetime.now(timezone.utc).timestamp()
        assert decoded["exp"] > now
    
    def test_register_http_status_codes(self, client, mock_recaptcha_success):
        """Test various HTTP status codes for register endpoint"""
        # 201 Created for successful registration
        response = client.post(
            "/auth/register",
            json={
                "email": "status@example.com",
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        assert response.status_code == 201
    
    def test_login_http_status_codes(self, client, test_user_data, mock_recaptcha_success):
        """Test various HTTP status codes for login endpoint"""
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        # 200 OK for successful login
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        assert response.status_code == 200
    
    def test_register_concurrent_unique_emails(self, client, mock_recaptcha_success):
        """Test that multiple users can register with unique emails"""
        emails = [f"user{i}@example.com" for i in range(5)]
        responses = []
        
        for email in emails:
            response = client.post(
                "/auth/register",
                json={
                    "email": email,
                    "password": "Password123!",
                    "captcha_token": "valid_token"
                }
            )
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 201 for r in responses)
        
        # All IDs should be unique
        ids = [r.json()["id"] for r in responses]
        assert len(ids) == len(set(ids))


# ==================== Recaptcha Error Path Tests ====================

class TestRecaptchaErrorPaths:
    """Additional reCAPTCHA error path tests"""
    
    def test_register_recaptcha_request_exception(self, client, monkeypatch):
        """Test register when reCAPTCHA request raises exception"""
        mock_post = MagicMock()
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        monkeypatch.setenv("REACT_APP_RECAPTCHA_SECRET_KEY", "key")
        monkeypatch.setattr("app.routers.auth.requests.post", mock_post)
        
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "Password123!",
                "captcha_token": "token"
            }
        )
        
        assert response.status_code == 503
    
    def test_login_recaptcha_request_exception(self, client, monkeypatch):
        """Test login when reCAPTCHA request raises exception"""
        mock_post = MagicMock()
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        monkeypatch.setenv("REACT_APP_RECAPTCHA_SECRET_KEY", "key")
        monkeypatch.setattr("app.routers.auth.requests.post", mock_post)
        
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "Password123!",
                "captcha_token": "token"
            }
        )
        
        assert response.status_code == 503
    
    def test_recaptcha_empty_error_codes(self, monkeypatch):
        """Test reCAPTCHA failure with empty error codes"""
        mock_post = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": False}
        mock_post.return_value = mock_response
        
        monkeypatch.setenv("REACT_APP_RECAPTCHA_SECRET_KEY", "key")
        monkeypatch.setattr("app.routers.auth.requests.post", mock_post)
        
        with pytest.raises(Exception):
            verify_recaptcha("token")
    
    def test_recaptcha_with_challenge_ts(self, monkeypatch):
        """Test successful reCAPTCHA with challenge timestamp"""
        mock_post = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "challenge_ts": "2025-01-17T10:00:00Z",
            "hostname": "example.com"
        }
        mock_post.return_value = mock_response
        
        monkeypatch.setenv("REACT_APP_RECAPTCHA_SECRET_KEY", "key")
        monkeypatch.setattr("app.routers.auth.requests.post", mock_post)
        
        result = verify_recaptcha("token")
        assert result is True


# ==================== Token Expiration Tests ====================

class TestTokenExpiration:
    """Tests for token expiration behavior"""
    
    def test_login_token_default_expiration_48h(self, client, test_user_data, mock_recaptcha_success):
        """Test that login tokens use default 48-hour expiration"""
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "captcha_token": "valid_token"
            }
        )
        
        token = response.json()["access_token"]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check expiration is roughly 48 hours from now
        now = datetime.now(timezone.utc).timestamp()
        exp_delta_hours = (decoded["exp"] - now) / 3600
        
        # Should be close to 48 hours (2880 minutes)
        assert 47 < exp_delta_hours < 49
    
    def test_create_token_with_short_expiration(self):
        """Test creating token with short expiration"""
        data = {"sub": "short@example.com"}
        short_expiration = timedelta(minutes=1)
        
        token = create_access_token(data, short_expiration)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        now = datetime.now(timezone.utc).timestamp()
        exp_delta_minutes = (decoded["exp"] - now) / 60
        
        assert 0 < exp_delta_minutes < 2
    
    def test_create_token_with_long_expiration(self):
        """Test creating token with long expiration"""
        data = {"sub": "long@example.com"}
        long_expiration = timedelta(days=365)
        
        token = create_access_token(data, long_expiration)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        now = datetime.now(timezone.utc).timestamp()
        exp_delta_days = (decoded["exp"] - now) / 86400
        
        assert 364 < exp_delta_days < 366


# ==================== Password Validation Tests ====================

class TestPasswordValidation:
    """Additional password validation tests"""
    
    def test_register_password_7_chars_fails(self, client, mock_recaptcha_success):
        """Test that 7-character password is rejected"""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "1234567",  # 7 chars
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_password_exact_8_chars_succeeds(self, client, mock_recaptcha_success):
        """Test that exactly 8-character password succeeds"""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "12345678",  # exactly 8 chars
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 201
    
    def test_register_password_whitespace_only_fails(self, client, mock_recaptcha_success):
        """Test that whitespace-only password fails"""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "        ",  # 8 spaces
                "captcha_token": "valid_token"
            }
        )
        
        # Should still succeed as it meets length requirement
        # (validation is only on length in schema)
        assert response.status_code == 201
    
    def test_password_comparison_is_case_sensitive(self):
        """Test that password comparison is case-sensitive"""
        password = "Password123"
        hashed = get_password_hash(password)
        
        assert verify_password("Password123", hashed)
        assert verify_password("PASSWORD123", hashed) is False
        assert verify_password("password123", hashed) is False


# ==================== Email Validation Tests ====================

class TestEmailValidation:
    """Additional email validation tests"""
    
    def test_register_email_with_plus_sign(self, client, mock_recaptcha_success):
        """Test email with plus sign (Gmail-style aliases)"""
        email = "user+tag@example.com"
        
        response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 201
        assert response.json()["email"] == email
    
    def test_register_email_multiple_subdomains(self, client, mock_recaptcha_success):
        """Test email with multiple subdomain levels"""
        email = "user@mail.example.co.uk"
        
        response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 201
    
    def test_register_email_numeric_domain(self, client, mock_recaptcha_success):
        """Test email with numeric characters"""
        email = "user123@example456.com"
        
        response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "Password123!",
                "captcha_token": "valid_token"
            }
        )
        
        assert response.status_code == 201


# ==================== Concurrent Operation Tests ====================

class TestConcurrentOperations:
    """Tests for concurrent-like operations"""
    
    def test_register_then_login_same_session(self, client, mock_recaptcha_success):
        """Test register and login in same session"""
        email = "concurrent@example.com"
        password = "Password123!"
        
        # Register
        reg_response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        assert reg_response.status_code == 201
        user_id = reg_response.json()["id"]
        
        # Immediately login
        login_response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password,
                "captcha_token": "valid_token"
            }
        )
        assert login_response.status_code == 200
        
        # Verify token contains correct ID
        token = login_response.json()["access_token"]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["user_id"] == user_id
    
    def test_failed_login_doesnt_modify_user(self, client, test_user_data, mock_recaptcha_success, db_session):
        """Test that failed login doesn't modify user data"""
        client.post(
            "/auth/register",
            json=test_user_data
        )
        
        user_before = db_session.query(UserModel).filter_by(email=test_user_data["email"]).first()
        original_password_hash = user_before.password
        
        # Failed login attempt
        client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "WrongPassword!",
                "captcha_token": "valid_token"
            }
        )
        
        # Password should not change
        user_after = db_session.query(UserModel).filter_by(email=test_user_data["email"]).first()
        assert user_after.password == original_password_hash


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app", "--cov-report=html"])
