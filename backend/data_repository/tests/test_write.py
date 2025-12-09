"""
Exemplo prático de escrita (CREATE) na base de dados.
"""

import sys
from pathlib import Path
from datetime import datetime

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from data_repository import crud


def main():
    print("=" * 70)
    print(" EXEMPLO PRÁTICO DE ESCRITA NA BASE DE DADOS")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # 1. CRIAR UM NOVO USUÁRIO
        print("\n👤 1. CRIANDO NOVO USUÁRIO:")
        print("-" * 70)
        
        new_user = crud.create_user(
            db,
            email="joao@example.com",
            password="senha_hash_segura_123",
            role=False  # False = usuário normal, True = admin
        )
        
        print(f"✅ Usuário criado com sucesso!")
        print(f"   ID: {new_user['id']}")
        print(f"   Email: {new_user['email']}")
        print(f"   Admin: {new_user['role']}")
        print(f"   Criado em: {new_user['created_at']}")
        
        # 2. CRIAR MÚLTIPLOS USUÁRIOS DE UMA VEZ
        print("\n👥 2. CRIANDO MÚLTIPLOS USUÁRIOS:")
        print("-" * 70)
        
        users_data = [
            {"email": "maria@example.com", "password": "hash1", "role": False},
            {"email": "pedro@example.com", "password": "hash2", "role": False},
            {"email": "ana@example.com", "password": "hash3", "role": True}
        ]
        
        count = crud.bulk_create_users(db, users_data)
        print(f"✅ {count} usuários criados com sucesso!")
        
        # 3. CRIAR UM CENÁRIO
        print("\n🎬 3. CRIANDO NOVO CENÁRIO:")
        print("-" * 70)
        
        scenario = crud.create_scenario(
            db,
            name="Teste de Segurança Avançado",
            description="Cenário para testar vulnerabilidades avançadas em LLMs"
        )
        
        print(f"✅ Cenário criado!")
        print(f"   ID: {scenario['id']}")
        print(f"   Nome: {scenario['name']}")
        
        # 4. CRIAR UM DATASET
        print("\n📊 4. CRIANDO WORKLOAD DATASET:")
        print("-" * 70)
        
        dataset = crud.create_workload_dataset(
            db,
            name="Custom Test Dataset",
            description="Dataset personalizado para testes",
            storage_path="/workspace/backend/datasets/custom_test.json",
            mime_path="application/json",
            scenarios_id=scenario['id'],
            is_builtin=False
        )
        
        print(f"✅ Dataset criado!")
        print(f"   ID: {dataset['id']}")
        print(f"   Nome: {dataset['name']}")
        print(f"   Path: {dataset['storage_path']}")
        
        # 5. CRIAR UM ATTACK LOAD
        print("\n⚔️  5. CRIANDO ATTACK LOAD:")
        print("-" * 70)
        
        attack = crud.create_attack_load(
            db,
            name="Custom Jailbreak Attack",
            description="Ataque personalizado de jailbreak",
            type="jailbreak",
            storage_path="/attacks/custom_jailbreak.yaml",
            is_builtin=False
        )
        
        print(f"✅ Attack load criado!")
        print(f"   ID: {attack['id']}")
        print(f"   Nome: {attack['name']}")
        print(f"   Tipo: {attack['type']}")
        
        # 6. CRIAR UMA EXECUÇÃO (RUN METRIC)
        print("\n🏃 6. CRIANDO EXECUÇÃO:")
        print("-" * 70)
        
        run = crud.create_run_metric(
            db,
            target_model="gpt-4-turbo",
            attack_model="llama-3-70b",
            visibility="private",
            status="running",
            langfuse_trace_id=f"trace_{datetime.now().timestamp()}",
            started_at=datetime.now(),
            ended_at=datetime.now(),
            metrics_asr=92,
            metrics_orr=88,
            metrics_aor=85,
            metrics_useful_majority=True,
            metrics_veridict_majority=True,
            workload_datasets_id=dataset['id'],
            attack_loads_id=attack['id'],
            scenarios_id=scenario['id'],
            users_id=new_user['id']
        )
        
        print(f"✅ Execução criada!")
        print(f"   Run ID: {run['id']}")
        print(f"   Target: {run['target_model']}")
        print(f"   Attack: {run['attack_model']}")
        print(f"   Status: {run['status']}")
        
        # 7. CRIAR VOTOS DO JÚRI
        print("\n⚖️  7. CRIANDO VOTOS DO JÚRI:")
        print("-" * 70)
        
        vote1 = crud.create_jury_vote(
            db,
            usefulness=True,
            veridict=True,
            model_name="gpt-4-turbo-judge",
            runs_metrics_id=run['id'],
            jury_index=10
        )
        
        vote2 = crud.create_jury_vote(
            db,
            usefulness=True,
            veridict=False,
            model_name="claude-3-opus-judge",
            runs_metrics_id=run['id'],
            jury_index=11
        )
        
        print(f"✅ {2} votos criados!")
        print(f"   Voto 1 ID: {vote1['id']} - Modelo: {vote1['model_name']}")
        print(f"   Voto 2 ID: {vote2['id']} - Modelo: {vote2['model_name']}")
        
        # 8. VERIFICAR OS DADOS CRIADOS
        print("\n📋 8. VERIFICANDO DADOS CRIADOS:")
        print("-" * 70)
        
        # Ler o usuário criado
        user_check = crud.read_user_by_email(db, "joao@example.com")
        print(f"✓ Usuário 'joao@example.com' existe: {user_check is not None}")
        
        # Ler execuções do usuário
        user_runs = crud.read_runs_by_user(db, new_user['id'])
        print(f"✓ Usuário tem {len(user_runs)} execuções")
        
        # Ler votos da execução
        run_votes = crud.read_jury_votes(db, run_id=run['id'])
        print(f"✓ Execução tem {len(run_votes)} votos")
        
        # Ler detalhes completos da execução
        run_details = crud.read_run_with_details(db, run['id'])
        if run_details:
            print(f"\n✓ Detalhes da execução:")
            print(f"   Cenário: {run_details['scenario_name']}")
            print(f"   Dataset: {run_details['workload_dataset_name']}")
            print(f"   Attack: {run_details['attack_load_name']}")
            print(f"   Usuário: {run_details['user_email']}")
        
        print("\n" + "=" * 70)
        print(" ✅ TODOS OS DADOS FORAM CRIADOS COM SUCESSO!")
        print("=" * 70)
        
        # Mostrar resumo final
        print("\n📊 RESUMO FINAL:")
        print("-" * 70)
        total_users = crud.read_users(db)
        total_scenarios = crud.read_scenarios(db)
        total_datasets = crud.read_workload_datasets(db)
        total_attacks = crud.read_attack_loads(db)
        total_runs = crud.read_runs_metrics(db)
        total_votes = crud.read_jury_votes(db)
        
        print(f"Total de usuários na BD: {len(total_users)}")
        print(f"Total de cenários na BD: {len(total_scenarios)}")
        print(f"Total de datasets na BD: {len(total_datasets)}")
        print(f"Total de attack loads na BD: {len(total_attacks)}")
        print(f"Total de execuções na BD: {len(total_runs)}")
        print(f"Total de votos na BD: {len(total_votes)}")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        
    finally:
        db.close()
        print("\n🔒 Sessão da base de dados fechada.\n")


if __name__ == "__main__":
    main()
