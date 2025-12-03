"""
Script para testar as funções CRUD da base de dados.
Execute com: python -m backend.test_crud (a partir da raiz do workspace)
ou: python test_crud.py (a partir de /workspace/backend)
"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from data_repository import crud


def print_section(title: str):
    """Imprime um título de seção formatado."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_read_users():
    """Testa a leitura de usuários."""
    print_section("TESTANDO LEITURA DE USUÁRIOS")
    
    db = SessionLocal()
    try:
        # Ler todos os usuários
        users = crud.read_users(db, limit=5)
        print(f"\n✓ Total de usuários encontrados (limite 5): {len(users)}")
        
        if users:
            print("\nPrimeiro usuário:")
            for key, value in users[0].items():
                print(f"  {key}: {value}")
            
            # Testar leitura por ID
            user_id = users[0]['id']
            user = crud.read_user_by_id(db, user_id)
            print(f"\n✓ Usuário por ID {user_id}: {user['email'] if user else 'Não encontrado'}")
            
            # Testar leitura por email
            if user:
                user_by_email = crud.read_user_by_email(db, user['email'])
                print(f"✓ Usuário por email: {user_by_email['email'] if user_by_email else 'Não encontrado'}")
        else:
            print("⚠ Nenhum usuário encontrado na base de dados")
            
    except Exception as e:
        print(f"✗ Erro ao ler usuários: {e}")
    finally:
        db.close()


def test_read_scenarios():
    """Testa a leitura de cenários."""
    print_section("TESTANDO LEITURA DE CENÁRIOS")
    
    db = SessionLocal()
    try:
        scenarios = crud.read_scenarios(db)
        print(f"\n✓ Total de cenários encontrados: {len(scenarios)}")
        
        if scenarios:
            print("\nCenários disponíveis:")
            for scenario in scenarios:
                print(f"  - ID {scenario['id']}: {scenario['name']}")
            
            # Testar leitura por ID
            scenario_id = scenarios[0]['id']
            scenario = crud.read_scenario_by_id(db, scenario_id)
            if scenario:
                print(f"\n✓ Detalhes do cenário {scenario_id}:")
                print(f"  Nome: {scenario['name']}")
                print(f"  Descrição: {scenario['description']}")
        else:
            print("⚠ Nenhum cenário encontrado na base de dados")
            
    except Exception as e:
        print(f"✗ Erro ao ler cenários: {e}")
    finally:
        db.close()


def test_read_runs():
    """Testa a leitura de execuções."""
    print_section("TESTANDO LEITURA DE EXECUÇÕES")
    
    db = SessionLocal()
    try:
        # Ler execuções recentes
        recent_runs = crud.read_recent_runs(db, limit=5)
        print(f"\n✓ Total de execuções recentes: {len(recent_runs)}")
        
        if recent_runs:
            print("\nExecuções recentes:")
            for run in recent_runs:
                print(f"\n  Run ID {run['id']}:")
                print(f"    Status: {run['status']}")
                print(f"    Modelo alvo: {run['target_model']}")
                print(f"    Modelo ataque: {run['attack_model']}")
                print(f"    Iniciado em: {run['started_at']}")
                print(f"    Usuário: {run['user_email']}")
            
            # Testar leitura com detalhes
            run_id = recent_runs[0]['id']
            run_details = crud.read_run_with_details(db, run_id)
            if run_details:
                print(f"\n✓ Detalhes completos da execução {run_id}:")
                print(f"  Cenário: {run_details.get('scenario_name', 'N/A')}")
                print(f"  Dataset: {run_details.get('workload_dataset_name', 'N/A')}")
                print(f"  Attack Load: {run_details.get('attack_load_name', 'N/A')}")
        else:
            print("⚠ Nenhuma execução encontrada na base de dados")
            
    except Exception as e:
        print(f"✗ Erro ao ler execuções: {e}")
    finally:
        db.close()


def test_read_workload_datasets():
    """Testa a leitura de datasets de workload."""
    print_section("TESTANDO LEITURA DE WORKLOAD DATASETS")
    
    db = SessionLocal()
    try:
        datasets = crud.read_workload_datasets(db)
        print(f"\n✓ Total de datasets encontrados: {len(datasets)}")
        
        if datasets:
            print("\nDatasets disponíveis:")
            for dataset in datasets[:5]:  # Mostrar apenas 5
                print(f"  - ID {dataset['id']}: {dataset['name']}")
                print(f"    Path: {dataset['storage_path']}")
                print(f"    Built-in: {dataset['is_builtin']}")
        else:
            print("⚠ Nenhum dataset encontrado na base de dados")
            
    except Exception as e:
        print(f"✗ Erro ao ler datasets: {e}")
    finally:
        db.close()


def test_read_attack_loads():
    """Testa a leitura de cargas de ataque."""
    print_section("TESTANDO LEITURA DE ATTACK LOADS")
    
    db = SessionLocal()
    try:
        attacks = crud.read_attack_loads(db)
        print(f"\n✓ Total de attack loads encontrados: {len(attacks)}")
        
        if attacks:
            print("\nAttack loads disponíveis:")
            for attack in attacks[:5]:  # Mostrar apenas 5
                print(f"  - ID {attack['id']}: {attack['name']}")
                print(f"    Tipo: {attack['type']}")
                print(f"    Built-in: {attack['is_builtin']}")
        else:
            print("⚠ Nenhum attack load encontrado na base de dados")
            
    except Exception as e:
        print(f"✗ Erro ao ler attack loads: {e}")
    finally:
        db.close()


def test_read_jury_votes():
    """Testa a leitura de votos do júri."""
    print_section("TESTANDO LEITURA DE JURY VOTES")
    
    db = SessionLocal()
    try:
        votes = crud.read_jury_votes(db)
        print(f"\n✓ Total de votos encontrados: {len(votes)}")
        
        if votes:
            print("\nPrimeiros votos:")
            for vote in votes[:3]:  # Mostrar apenas 3
                print(f"\n  Voto ID {vote['id']}:")
                print(f"    Run ID: {vote['runs_metrics_id']}")
                print(f"    Modelo: {vote['model_name']}")
                print(f"    Útil: {vote['usefulness']}")
                print(f"    Veredito: {vote.get('veridict', 'N/A')}")
        else:
            print("⚠ Nenhum voto encontrado na base de dados")
            
    except Exception as e:
        print(f"✗ Erro ao ler votos: {e}")
    finally:
        db.close()


def test_generic_functions():
    """Testa as funções genéricas."""
    print_section("TESTANDO FUNÇÕES GENÉRICAS")
    
    db = SessionLocal()
    try:
        # Testar read_all_from_table
        models = crud.read_all_from_table(db, "models")
        print(f"\n✓ Modelos (via função genérica): {len(models)}")
        if models:
            print(f"  Primeiros modelos: {[m.get('name') for m in models[:3]]}")
        
    except Exception as e:
        print(f"✗ Erro ao testar funções genéricas: {e}")
    finally:
        db.close()


def main():
    """Função principal que executa todos os testes."""
    print("\n" + "╔" + "═"*58 + "╗")
    print("║" + " "*15 + "TESTE DAS FUNÇÕES CRUD" + " "*21 + "║")
    print("╚" + "═"*58 + "╝")
    
    try:
        # Executar todos os testes
        test_read_users()
        test_read_scenarios()
        test_read_runs()
        test_read_workload_datasets()
        test_read_attack_loads()
        test_read_jury_votes()
        test_generic_functions()
        
        print_section("TESTES CONCLUÍDOS")
        print("\n✓ Todos os testes foram executados!")
        print("\nNota: Se alguma seção mostrou '⚠ Nenhum ... encontrado',")
        print("      isso significa que a tabela existe mas está vazia.\n")
        
    except Exception as e:
        print(f"\n✗ Erro fatal durante os testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
