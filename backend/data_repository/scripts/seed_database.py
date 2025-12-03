"""
Script para popular a base de dados com dados de exemplo.
Execute com: python seed_database.py
"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from data_repository import crud
from datetime import datetime


def print_section(title: str):
    """Imprime um título de seção formatado."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def seed_with_function():
    """Usa a função seed_database para popular a BD."""
    print_section("POPULANDO BASE DE DADOS COM FUNÇÃO SEED")
    
    db = SessionLocal()
    try:
        counts = crud.seed_database(db)
        print("\n✓ Base de dados populada com sucesso!")
        print("\nRegistros criados:")
        for table, count in counts.items():
            print(f"  - {table}: {count}")
        
        return True
    except Exception as e:
        print(f"\n✗ Erro ao popular BD: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def seed_manually():
    """Cria dados manualmente usando funções individuais."""
    print_section("POPULANDO BASE DE DADOS MANUALMENTE")
    
    db = SessionLocal()
    try:
        # 1. Criar usuários
        print("\n1. Criando usuários...")
        user1 = crud.create_user(
            db,
            email="test_admin@example.com",
            password="admin_password_hash",
            role=True
        )
        print(f"   ✓ Admin criado: {user1['email']} (ID: {user1['id']})")
        
        user2 = crud.create_user(
            db,
            email="test_user@example.com",
            password="user_password_hash",
            role=False
        )
        print(f"   ✓ Usuário criado: {user2['email']} (ID: {user2['id']})")
        
        # 2. Criar cenários
        print("\n2. Criando cenários...")
        scenario1 = crud.create_scenario(
            db,
            name="Prompt Injection Test",
            description="Cenário para testar ataques de prompt injection"
        )
        print(f"   ✓ Cenário criado: {scenario1['name']} (ID: {scenario1['id']})")
        
        scenario2 = crud.create_scenario(
            db,
            name="Jailbreak Test",
            description="Cenário para testar tentativas de jailbreak"
        )
        print(f"   ✓ Cenário criado: {scenario2['name']} (ID: {scenario2['id']})")
        
        # 3. Criar workload datasets
        print("\n3. Criando workload datasets...")
        dataset1 = crud.create_workload_dataset(
            db,
            name="Malicious Goals Dataset",
            description="Dataset com objetivos maliciosos",
            storage_path="/workspace/backend/datasets/malicious_goals.json",
            mime_path="application/json",
            scenarios_id=scenario1['id'],
            is_builtin=True
        )
        print(f"   ✓ Dataset criado: {dataset1['name']} (ID: {dataset1['id']})")
        
        dataset2 = crud.create_workload_dataset(
            db,
            name="Vulnerable Goals Dataset",
            description="Dataset com objetivos vulneráveis",
            storage_path="/workspace/backend/datasets/vulnerable_goals.json",
            mime_path="application/json",
            scenarios_id=scenario1['id'],
            is_builtin=True
        )
        print(f"   ✓ Dataset criado: {dataset2['name']} (ID: {dataset2['id']})")
        
        # 4. Criar attack loads
        print("\n4. Criando attack loads...")
        attack1 = crud.create_attack_load(
            db,
            name="CRESCENDO Attack",
            description="Ataque de escalação gradual que aumenta a complexidade",
            type="crescendo",
            storage_path="/attacks/crescendo.yaml",
            is_builtin=True
        )
        print(f"   ✓ Attack load criado: {attack1['name']} (ID: {attack1['id']})")
        
        attack2 = crud.create_attack_load(
            db,
            name="MR Robot Attack",
            description="Ataque baseado em personagem para bypass",
            type="mr_robot",
            storage_path="/attacks/mr_robot.yaml",
            is_builtin=True
        )
        print(f"   ✓ Attack load criado: {attack2['name']} (ID: {attack2['id']})")
        
        # 5. Criar uma execução de exemplo
        print("\n5. Criando execução de teste...")
        run = crud.create_run_metric(
            db,
            target_model="gpt-4",
            attack_model="gemma-3-27b",
            visibility="public",
            status="completed",
            langfuse_trace_id="trace_123456789",
            started_at=datetime.now(),
            ended_at=datetime.now(),
            metrics_asr=75,
            metrics_orr=80,
            metrics_aor=70,
            metrics_useful_majority=True,
            metrics_veridict_majority=False,
            workload_datasets_id=dataset1['id'],
            attack_loads_id=attack1['id'],
            scenarios_id=scenario1['id'],
            users_id=user1['id']
        )
        print(f"   ✓ Execução criada (ID: {run['id']})")
        
        # 6. Criar votos do júri
        print("\n6. Criando votos do júri...")
        vote1 = crud.create_jury_vote(
            db,
            usefulness=True,
            veridict=True,
            model_name="gpt-4-judge",
            runs_metrics_id=run['id'],
            jury_index=1
        )
        print(f"   ✓ Voto do júri criado (ID: {vote1['id']})")
        
        vote2 = crud.create_jury_vote(
            db,
            usefulness=True,
            veridict=False,
            model_name="claude-judge",
            runs_metrics_id=run['id'],
            jury_index=2
        )
        print(f"   ✓ Voto do júri criado (ID: {vote2['id']})")
        
        print("\n" + "="*60)
        print("✓ Base de dados populada com sucesso!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Erro ao popular BD: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def verify_data():
    """Verifica os dados criados."""
    print_section("VERIFICANDO DADOS CRIADOS")
    
    db = SessionLocal()
    try:
        users = crud.read_users(db)
        scenarios = crud.read_scenarios(db)
        datasets = crud.read_workload_datasets(db)
        attacks = crud.read_attack_loads(db)
        runs = crud.read_runs_metrics(db)
        votes = crud.read_jury_votes(db)
        
        print(f"\n✓ Usuários: {len(users)}")
        for user in users:
            print(f"   - {user['email']} (admin: {user['role']})")
        
        print(f"\n✓ Cenários: {len(scenarios)}")
        for scenario in scenarios:
            print(f"   - {scenario['name']}")
        
        print(f"\n✓ Workload Datasets: {len(datasets)}")
        for dataset in datasets:
            print(f"   - {dataset['name']}")
        
        print(f"\n✓ Attack Loads: {len(attacks)}")
        for attack in attacks:
            print(f"   - {attack['name']} (tipo: {attack['type']})")
        
        print(f"\n✓ Execuções: {len(runs)}")
        for run in runs:
            print(f"   - Run {run['id']}: {run['target_model']} vs {run['attack_model']}")
        
        print(f"\n✓ Votos do Júri: {len(votes)}")
        for vote in votes:
            print(f"   - Voto {vote['id']}: {vote['model_name']} (útil: {vote['usefulness']})")
        
    except Exception as e:
        print(f"\n✗ Erro ao verificar dados: {e}")
    finally:
        db.close()


def main():
    """Função principal."""
    print("\n" + "╔" + "═"*58 + "╗")
    print("║" + " "*12 + "POPULAR BASE DE DADOS COM DADOS DE TESTE" + " "*6 + "║")
    print("╚" + "═"*58 + "╝")
    
    print("\nEscolha uma opção:")
    print("1. Usar função seed_database() automática")
    print("2. Popular manualmente (mais detalhado)")
    print("3. Apenas verificar dados existentes")
    
    choice = input("\nOpção (1/2/3 ou Enter para usar opção 2): ").strip()
    
    if choice == "1":
        success = seed_with_function()
    elif choice == "3":
        verify_data()
        return
    else:  # Padrão: opção 2
        success = seed_manually()
    
    if success:
        print("\n")
        verify_data()


if __name__ == "__main__":
    main()
