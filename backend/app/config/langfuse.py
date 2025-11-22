"""
Configuração do Langfuse para tracing de LLMs.

Uso:
    from app.config.langfuse import get_langfuse_client
    
    langfuse = get_langfuse_client()
    if langfuse:
        trace = langfuse.trace(name="my-llm-call")
"""

import os
from typing import Optional
from langfuse import Langfuse


class LangfuseConfig:
    """Configuração centralizada do Langfuse."""
    
    def __init__(self):
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        self.host = os.getenv("LANGFUSE_HOST", "http://langfuse-web:3000")
        self.enabled = os.getenv("LANGFUSE_ENABLED", "true").lower() == "true"
        self._client: Optional[Langfuse] = None
    
    @property
    def client(self) -> Optional[Langfuse]:
        """
        Retorna cliente Langfuse (lazy loading).
        Retorna None se não estiver configurado ou desabilitado.
        """
        if not self.enabled:
            return None
            
        if self._client is None:
            if not self.public_key or not self.secret_key:
                print("⚠️  Langfuse não configurado. Define LANGFUSE_PUBLIC_KEY e LANGFUSE_SECRET_KEY")
                return None
            
            try:
                self._client = Langfuse(
                    public_key=self.public_key,
                    secret_key=self.secret_key,
                    host=self.host
                )
                print(f"✅ Langfuse configurado: {self.host}")
            except Exception as e:
                print(f"❌ Erro ao configurar Langfuse: {e}")
                return None
        
        return self._client
    
    def flush(self):
        """Flush pending events (chamar no shutdown da app)."""
        if self._client:
            self._client.flush()


# Singleton global
_langfuse_config = LangfuseConfig()


def get_langfuse_client() -> Optional[Langfuse]:
    """
    Retorna o cliente Langfuse configurado.
    
    Returns:
        Cliente Langfuse ou None se não estiver configurado.
    """
    return _langfuse_config.client


def flush_langfuse():
    """Flush eventos pendentes do Langfuse."""
    _langfuse_config.flush()
