"""
Exemplo prático de leitura da base de dados.
"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from data_repository import crud


def main():
    print("=" * 70)
    print(" EXEMPLO PRÁTICO DE LEITURA DA BASE DE DADOS")
    print("=" * 70)
    
    # Criar sessão da base de dados
    db = SessionLocal()
    
    try:
        # 1. LER TODOS OS USUÁRIOS
        print("\n📋 1. LENDO TODOS OS USUÁRIOS:")
        print("-" * 70)
        users = crud.read_users(db)
        print(f"Total de usuários encontrados: {len(users)}\n")
        
        for user in users:
            print(f"  • ID: {user['id']}")
            print(f"    Email: {user['email']}")
            print(f"    Admin: {'Sim' if user['role'] else 'Não'}")
            print(f"    Criado em: {user['created_at']}")
            print()
        
        # 2. LER USUÁRIO ESPECÍFICO POR ID
        if users:
            print("\n🔍 2. LENDO USUÁRIO ESPECÍFICO (ID=1):")
            print("-" * 70)
            user = crud.read_user_by_id(db, 1)
            if user:
                print(f"Email: {user['email']}")
                print(f"Role: {user['role']}")
            else:
                print("Usuário não encontrado!")
        
        # 3. LER USUÁRIO POR EMAIL
        print("\n📧 3. BUSCANDO USUÁRIO POR EMAIL:")
        print("-" * 70)
        user = crud.read_user_by_email(db, "admin@example.com")
        if user:
            print(f"Encontrado! ID: {user['id']}, Email: {user['email']}")
        else:
            print("Usuário não encontrado!")
        
        # 4. LER CENÁRIOS
        print("\n🎬 4. LENDO TODOS OS CENÁRIOS:")
        print("-" * 70)
        scenarios = crud.read_scenarios(db)
        print(f"Total de cenários: {len(scenarios)}\n")
        
        for scenario in scenarios:
            print(f"  • ID {scenario['id']}: {scenario['name']}")
            print(f"    Descrição: {scenario['description']}")
            print()
        
        # 5. LER DATASETS
        print("\n📊 5. LENDO WORKLOAD DATASETS:")
        print("-" * 70)
        datasets = crud.read_workload_datasets(db)
        print(f"Total de datasets: {len(datasets)}\n")
        
        for dataset in datasets:
            print(f"  • ID {dataset['id']}: {dataset['name']}")
            print(f"    Path: {dataset['storage_path']}")
            print(f"    Built-in: {'Sim' if dataset['is_builtin'] else 'Não'}")
            print(f"    Cenário ID: {dataset['scenarios_id']}")
            print()
        
        # 6. LER ATTACK LOADS
        print("\n⚔️  6. LENDO ATTACK LOADS:")
        print("-" * 70)
        attacks = crud.read_attack_loads(db)
        print(f"Total de attack loads: {len(attacks)}\n")
        
        for attack in attacks:
            print(f"  • ID {attack['id']}: {attack['name']}")
            print(f"    Tipo: {attack['type']}")
            print(f"    Descrição: {attack['description']}")
            print(f"    Built-in: {'Sim' if attack['is_builtin'] else 'Não'}")
            print()
        
        # 7. LER EXECUÇÕES RECENTES
        print("\n🏃 7. LENDO EXECUÇÕES RECENTES:")
        print("-" * 70)
        runs = crud.read_recent_runs(db, limit=10)
        
        if runs:
            print(f"Total de execuções: {len(runs)}\n")
            for run in runs:
                print(f"  • Run ID {run['id']}")
                print(f"    Status: {run['status']}")
                print(f"    Target Model: {run['target_model']}")
                print(f"    Attack Model: {run['attack_model']}")
                print(f"    ASR: {run['metrics_asr']}")
                print(f"    Usuário: {run['user_email']}")
                print(f"    Cenário: {run['scenario_name']}")
                print(f"    Iniciado: {run['started_at']}")
                print()
        else:
            print("Nenhuma execução encontrada.")
        
        # 8. LER VOTOS DO JÚRI
        print("\n⚖️  8. LENDO VOTOS DO JÚRI:")
        print("-" * 70)
        votes = crud.read_jury_votes(db)
        
        if votes:
            print(f"Total de votos: {len(votes)}\n")
            for vote in votes:
                print(f"  • Voto ID {vote['id']}")
                print(f"    Run ID: {vote['runs_metrics_id']}")
                print(f"    Modelo: {vote['model_name']}")
                print(f"    Útil: {'Sim' if vote['usefulness'] else 'Não'}")
                print(f"    Veredito: {vote.get('veridict', 'N/A')}")
                print()
        else:
            print("Nenhum voto encontrado.")
        
        # 9. EXEMPLO DE LEITURA COM FILTRO
        if users:
            print("\n👤 9. LENDO EXECUÇÕES DE UM USUÁRIO ESPECÍFICO:")
            print("-" * 70)
            user_id = users[0]['id']
            user_runs = crud.read_runs_by_user(db, user_id)
            print(f"Usuário {users[0]['email']} tem {len(user_runs)} execuções")
        
        # 10. FUNÇÃO GENÉRICA
        print("\n🔧 10. USANDO FUNÇÃO GENÉRICA (read_all_from_table):")
        print("-" * 70)
        all_scenarios = crud.read_all_from_table(db, "scenarios")
        print(f"Cenários via função genérica: {len(all_scenarios)}")
        
        print("\n" + "=" * 70)
        print(" ✅ LEITURA CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # IMPORTANTE: Sempre fechar a sessão!
        db.close()
        print("\n🔒 Sessão da base de dados fechada.")


if __name__ == "__main__":
    main()
