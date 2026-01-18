# GP_CTRL_plus_12 - Test Suite

Automated Red-Teaming of LLMs through Prompt-Based Attack Simulation

## Running Tests

### Prerequisites
Install test dependencies:
```bash
cd backend
pip install -r requirements-test.txt
```

### Run All Tests
```bash
pytest tests/test_auth.py -v
```

### Run Tests with Coverage Report
```bash
pytest tests/test_auth.py --cov=app --cov-report=html --cov-report=term-missing
```

### Run Specific Test Class
```bash
pytest tests/test_auth.py::TestPasswordFunctions -v
```

### Run Specific Test
```bash
pytest tests/test_auth.py::TestPasswordFunctions::test_verify_password_correct -v
```

## Test Coverage

The test suite covers authentication and security features with 112 comprehensive test cases across 17 test classes:

### Test Classes

1. **TestPasswordFunctions** - Password hashing and verification
   - Password hashing with bcrypt
   - Password verification
   - Edge cases (empty, very long, unicode passwords)

2. **TestAccessTokenCreation** - JWT token generation
   - Token creation with default/custom expiration
   - Token encoding/decoding
   - Expired token handling

3. **TestRegisterEndpoint** - User registration feature
   - Successful registration
   - Duplicate email prevention
   - Invalid input validation
   - reCAPTCHA verification

4. **TestLoginEndpoint** - User authentication
   - Successful login with valid credentials
   - Failed login with invalid credentials
   - Token generation on login
   - Email/password validation

5. **TestPasswordValidation** - Password policy enforcement
   - Minimum length requirement
   - Special character requirements
   - Format validation

6. **TestEmailValidation** - Email format validation
   - Valid email formats
   - Invalid email handling
   - Case sensitivity

7. **TestDatabaseInteractions** - Database operations
   - User creation and retrieval
   - Email uniqueness constraints
   - Role assignment
   - Timestamp handling

8. **TestAdditionalEndpointScenarios** - Extended endpoint testing
   - Multiple user registration
   - Token validity
   - Response schema validation
   - Concurrent operations

9. **TestRecaptchaErrorPaths** - reCAPTCHA error handling
   - Network failure handling
   - Invalid token response
   - Missing configuration
   - Error code parsing

10. **TestTokenExpiration** - Token lifecycle
    - Token expiration timing
    - Expired token rejection
    - Token refresh scenarios

11. **TestPasswordValidation** - Additional password tests
    - Special characters
    - Case sensitivity
    - Length constraints

12. **TestEmailValidation** - Additional email tests
    - Format validation
    - Normalization
    - Duplicate prevention

13. **TestConcurrentOperations** - Concurrent request handling
    - Multiple simultaneous registrations
    - Session isolation
    - Data integrity

14-17. **Additional Test Classes** - Schema validation, endpoint responses, security checks, and edge cases

### Coverage Targets

- **Line Coverage**: 80%+ target
- **Total Test Cases**: 112
- **Total Lines of Test Code**: 1,939
- **Production Code Tested**:
  - app/security.py - Password hashing, JWT token creation
  - app/routers/auth.py - Register, login, user profile endpoints
  - app/schemas.py - Pydantic models for request/response validation

### Test Output

Tests provide detailed feedback including:
- Pass/fail status
- Assertion messages
- Coverage metrics
- Performance timing
