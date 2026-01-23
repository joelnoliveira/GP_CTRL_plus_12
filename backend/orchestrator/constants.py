from enum import Enum

class TypesOfAttacks(str, Enum):
    CRESCENDO_ATTACK = "CRESCENDO_ATTACK"
    FLIP_ATTACK = "FLIP_ATTACK" 
    ROLE_PLAY_ATTACK = "ROLE_PLAY_ATTACK"
    TEMPLATE_ATTACK = "TEMPLATE_ATTACK"
    OVER_REFUSAL_ATTACK = "OVER_REFUSAL_ATTACK"
    ALL_ATTACKS = "ALL_ATTACKS"

class Goals(str, Enum):
    MALICIOUS_GOALS = "malicious_goals"
    VULNERABLE_GOALS = "vulnerable_goals"

class RolePlayOption(str, Enum):
    MR_ROBOT = "MR_ROBOT"
    VIDEO_GAME = "VIDEO_GAME"

class TargetModel(str, Enum):
    OLLAMA = "OLLAMA"
    OPEN_AI = "OPEN_AI"
    HUGGING_FACE = "HUGGING_FACE"
    AZURE = "AZURE_ML"

DEFAULTS = dict(
    seed=2316,
    temperature_judges=0.1,
    temperature_attacker=0.1,
    temperature_target=0.1,
    attacker_model_name="gemma3:27b",
    judge_model_name="gemma3:27b",
    jury_models=["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
    target_model_name="gemma3:27b",
    goals_list=None,
)
