from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from orchestrator.constants import TypesOfAttacks, Goals, RolePlayOption

# ============== Attack Schemas ==============

class AttackRequest(BaseModel):
    """Schema for the /attack endpoint"""
    attack_option: TypesOfAttacks = Field(..., description="Type of attack to execute")
    label: Goals = Field(default=Goals.MALICIOUS_GOALS, description="Dataset of goals to use")
    seed: int = Field(default=2316, description="Seed for reproducibility")
    temperature_judges: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for judge models")
    temperature_attacker: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for attacker models")
    temperature_target: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for target model")
    target_model_name: str = Field(default="gemma3:27b", description="Target model to attack")
    attacker_model_name: str = Field(default="gemma3:27b", description="Model that generates attacks")
    judge_model_name: str = Field(default="gemma3:27b", description="Judge model (for Crescendo/Flip)")
    jury_models: list[str] = Field(default=["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"], description="List of 3 jury models")
    role_play_option: Optional[RolePlayOption] = Field(default=RolePlayOption.MR_ROBOT, description="Role play scenario (only for ROLE_PLAY_ATTACK)")
    config_file_name: Optional[str] = Field(default=None, description="Name of a custom configuration file to use")
    goals_file_name: Optional[str] = Field(default=None, description="Name of an uploaded file containing custom goals")
    target_provider: Optional[str] = Field(default=None, description="Model provider for the target model (if required)")
    api_key: Optional[str] = Field(default=None, description="API key for the target model provider (if required)")
   
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "attack_option": "ROLE_PLAY_ATTACK",
                    "label": "malicious_goals",
                    "seed": 2316,
                    "temperature_judges": 0.1,
                    "temperature_attacker": 0.1,
                    "temperature_target": 0.1,
                    "target_model_name": "gemma3:27b",
                    "attacker_model_name": "gemma3:27b",
                    "judge_model_name": "gemma3:27b",
                    "jury_models": ["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
                    "role_play_option": "MR_ROBOT",
                    "goals_file_name": "custom_goals_20241230.json",
                    "target_provider": "OLLAMA",
                    "api_key": "sk-xxxx"
                }
            ]
        }
    }

class AttackTemplateRequest(BaseModel):
    """Schema for the /attack-template endpoint"""
    label: Goals = Field(default=Goals.MALICIOUS_GOALS, description="Dataset of goals to use")
    seed: int = Field(default=2316, description="Seed for reproducibility")
    temperature_judges: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for judge models")
    temperature_attacker: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for attacker models")
    temperature_target: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for target model")
    target_model_name: str = Field(default="gemma3:27b", description="Target model to attack")
    jury_models: list[str] = Field(default=["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"], description="List of 3 jury models")
    template_path: Optional[str] = Field(default=None, description="Path to the template file (optional)")
    target_provider: Optional[str] = Field(default=None, description="Model provider for the target model (if required)")
    api_key: Optional[str] = Field(default=None, description="API key for the target model provider (if required)")
    target_provider: Optional[str] = Field(default=None, description="Model provider for the target model (if required)")
    api_key: Optional[str] = Field(default=None, description="API key for the target model provider (if required)")
   
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "label": "malicious_goals",
                    "seed": 2316,
                    "temperature_judges": 0.1,
                    "temperature_attacker": 0.1,
                    "temperature_target": 0.1,
                    "target_model_name": "gemma3:27b",
                    "jury_models": ["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
                    "template_path": "/backend/datasets/JailBreakV_28K_clean.yaml",
                    "target_provider": "OLLAMA",
                    "api_key": "sk-xxxx"
                }
            ]
        }
    }

class OverRefusalTestRequest(BaseModel):
    """Schema for the /over-refusal-test endpoint"""
    seed: int = Field(default=2316, description="Seed for reproducibility")
    temperature_judges: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for judge models")
    temperature_attacker: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for attacker models")
    temperature_target: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for target model")
    target_model_name: str = Field(default="gemma3:27b", description="Target model to test")
    jury_models: list[str] = Field(default=["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"], description="List of 3 jury models")
    target_provider: Optional[str] = Field(default=None, description="Model provider for the target model (if required)")
    api_key: Optional[str] = Field(default=None, description="API key for the target model provider (if required)")
    target_provider: Optional[str] = Field(default=None, description="Model provider for the target model (if required)")
    api_key: Optional[str] = Field(default=None, description="API key for the target model provider (if required)")
   
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "seed": 2316,
                    "temperature_judges": 0.1,
                    "temperature_attacker": 0.1,
                    "temperature_target": 0.1,
                    "target_model_name": "gemma3:27b",
                    "jury_models": ["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
                    "target_provider": "OLLAMA",
                    "api_key": "sk-xxxx"
                }
            ]
        }
    }

# ============== User Schemas ==============

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    captcha_token: str

    #Input for swagger
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user1@example.com",
                    "password": "password",
                    "captcha_token": "token"
                }
            ]
        }
    }

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    captcha_token: str

    #Input for swagger
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user1@example.com",
                    "password": "password",
                    "captcha_token": "token"
                }
            ]
        }
    }

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
