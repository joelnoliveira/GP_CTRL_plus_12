from enum import Enum

class TypesOfAttacks(Enum):
    CRESCENDO_ATTACK = "CRESCENDO_ATTACK"
    FLIP_ATTACK = "FLIP_ATTACK" 
    ROLE_PLAY_ATTACK = "ROLE_PLAY_ATTACK"
    ALL_ATTACKS = "ALL_ATTACKS"

class Goals(Enum):
    MALICIOUS_GOALS = "malicious_goals"
    VULNERABLE_GOALS = "vulnerable_goals"

DEFAULTS = dict(
    seed=2316,
    temperature_judges=0.1,
    attacker_model_name="gemma3:27b",
    judge_model_name="gemma3:27b",
    jury_models=["deepseek-r1:70b", "qwen2.5:latest", "dolphin3:8b"],
    target_model_name="gemma3:27b",
    goals_list=None,
)
