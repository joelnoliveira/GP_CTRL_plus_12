"""Minimal .env loader with validation and normalization.

Usage:
    from config import *

Will populate os.environ and expose constants:
    LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST,
    OLLAMA_BASE_URL, OLLAMA_MODEL
"""
import os
from pathlib import Path

def _load_env(path: Path) -> None:
    if not path.exists():
        return
    with open(path) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value:
                os.environ.setdefault(key, value)

_load_env(Path(__file__).parent / '.env')

# Normalization / fallback (support legacy LANGFUSE_BASE_URL)
if 'LANGFUSE_HOST' not in os.environ and 'LANGFUSE_BASE_URL' in os.environ:
    os.environ['LANGFUSE_HOST'] = os.environ['LANGFUSE_BASE_URL']

LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')
LANGFUSE_HOST = os.getenv('LANGFUSE_HOST')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')

def _require(name: str, value: str | None):
    if not value:
        raise RuntimeError(f"Missing required config: {name}. Check .env")

_require('LANGFUSE_PUBLIC_KEY', LANGFUSE_PUBLIC_KEY)
_require('LANGFUSE_SECRET_KEY', LANGFUSE_SECRET_KEY)
_require('LANGFUSE_HOST', LANGFUSE_HOST)
_require('OLLAMA_BASE_URL', OLLAMA_BASE_URL)
_require('OLLAMA_MODEL', OLLAMA_MODEL)

# Optionally print a concise status (disable by default)
if os.getenv('CONFIG_DEBUG') == '1':
    print('[config] Loaded Langfuse host:', LANGFUSE_HOST)
