"""
Exemplo rápido de como usar as funções CRUD.
"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from data_repository import crud


# Exemplo 1: Ler todos os usuários
def exemplo_usuarios():
    db = SessionLocal()
    try:
        # Ler todos os usuários (com limite)
        usuarios = crud.read_users(db, limit=10)
        print(f"Total de usuários: {len(usuarios)}")
        
        # Ler usuário específico por ID
        if usuarios:
            usuario = crud.read_user_by_id(db, usuarios[0]['id'])
            print(f"Usuário: {usuario}")
            
            # Ler por email
            usuario_email = crud.read_user_by_email(db, usuario['email'])
            print(f"Usuário por email: {usuario_email}")
    finally:
        db.close()


# Exemplo 2: Ler execuções recentes
def exemplo_runs_recentes():
    db = SessionLocal()
    try:
        runs = crud.read_recent_runs(db, limit=5)
        for run in runs:
            print(f"Run {run['id']}: {run['status']} - {run['target_model']}")
    finally:
        db.close()


# Exemplo 3: Ler detalhes completos de uma execução
def exemplo_run_detalhado(run_id: int):
    db = SessionLocal()
    try:
        run = crud.read_run_with_details(db, run_id)
        if run:
            print(f"Cenário: {run['scenario_name']}")
            print(f"Dataset: {run['workload_dataset_name']}")
            print(f"Status: {run['status']}")
        else:
            print("Run não encontrado")
    finally:
        db.close()


# Exemplo 4: Ler todas as execuções de um usuário
def exemplo_runs_usuario(user_id: int):
    db = SessionLocal()
    try:
        runs = crud.read_runs_by_user(db, user_id)
        print(f"Usuário {user_id} tem {len(runs)} execuções")
        for run in runs:
            print(f"  - Run {run['id']}: {run['status']}")
    finally:
        db.close()


# Exemplo 5: Ler votos do júri de uma execução
def exemplo_jury_votes(run_id: int):
    db = SessionLocal()
    try:
        votes = crud.read_jury_votes(db, run_id=run_id)
        print(f"Execução {run_id} tem {len(votes)} votos")
        for vote in votes:
            print(f"  - Modelo {vote['model_name']}: útil={vote['usefulness']}")
    finally:
        db.close()


# Exemplo 6: Usar FastAPI dependency
from fastapi import Depends
from app.database import get_db

# No seu endpoint FastAPI:
# @app.get("/api/users")
# def get_users(db: Session = Depends(get_db)):
#     users = crud.read_users(db, limit=50)
#     return {"users": users}


if __name__ == "__main__":
    print("Executando exemplos...\n")
    exemplo_usuarios()
    print("\n" + "-"*50 + "\n")
    exemplo_runs_recentes()
