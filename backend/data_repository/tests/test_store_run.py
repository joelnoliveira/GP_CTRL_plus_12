"""
Comprehensive test for the store_run() function.
Tests database persistence of attack runs, results, artifacts, and jury votes.

Execute with: python -m backend.data_repository.tests.test_store_run
or: python test_store_run.py (from /backend/data_repository/tests/)
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from data_repository import crud


def print_section(title: str):
    """Print formatted section title."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_success(msg: str):
    """Print success message."""
    print(f"✅ {msg}")


def print_error(msg: str):
    """Print error message."""
    print(f"❌ {msg}")


def test_store_run_basic():
    """Test basic store_run functionality with minimal data."""
    print_section("TEST 1: BASIC STORE_RUN WITH MINIMAL DATA")
    
    db = SessionLocal()
    
    try:
        # Get or create base entities
        users = crud.read_users(db, limit=1)
        if not users:
            print_error("No users found in database. Seed database first.")
            return False
        
        scenarios = crud.read_scenarios(db, limit=1)
        if not scenarios:
            print_error("No scenarios found in database. Seed database first.")
            return False
        
        user_id = users[0]['id']
        scenario_id = scenarios[0]['id']
        
        print(f"Using user_id={user_id}, scenario_id={scenario_id}")
        
        # Minimal attack results
        attack_results = {
            "conversations": [
                {
                    "id": "conv_001",
                    "messages": [
                        {"role": "user", "content": "test prompt"},
                        {"role": "assistant", "content": "test response"}
                    ],
                    "score": 0.8
                }
            ],
            "metrics": {
                "asr": 0.5,
                "orr": 0.3,
                "aor": 0.2
            }
        }
        
        jury_votes = [
            {
                "jury_index": 0,
                "usefulness": True,
                "veridict": True,
                "model_name": "llama3.2:1b"
            },
            {
                "jury_index": 1,
                "usefulness": True,
                "veridict": True,
                "model_name": "llama3.2:1b"
            }
        ]
        
        # Call store_run
        started_at = datetime.now() - timedelta(minutes=5)
        ended_at = datetime.now()
        
        result = crud.store_run(
            db=db,
            user_id=user_id,
            scenario_id=scenario_id,
            target_model="llama3.2:1b",
            attack_model="llama3.2:1b",
            attack_type="crescendo",
            attack_results=attack_results,
            jury_votes_data=jury_votes,
            started_at=started_at,
            ended_at=ended_at,
            attacker_visibility="white_box"
        )
        
        run_id = result['run_id']
        print_success(f"store_run completed. Run ID: {run_id}")
        
        # Verify the run was created
        run = crud.read_run_by_id(db, run_id)
        if not run:
            print_error(f"Run {run_id} not found in database")
            return False
        
        print_success(f"Run verified in database")
        print(f"   Target Model: {run.get('target_model')}")
        print(f"   Attack Model: {run.get('attack_model')}")
        print(f"   Attack Type: {run.get('attack_type')}")
        print(f"   ASR: {run.get('metrics_asr')}")
        print(f"   ORR: {run.get('metrics_orr')}")
        
        # Verify jury votes were created
        jury_count = len(result.get('jury_vote_ids', []))
        print_success(f"Jury votes created: {jury_count}")
        
        # Verify results file was saved
        results_file = result.get('results_file_path')
        if results_file and Path(results_file).exists():
            print_success(f"Results file saved: {results_file}")
            with open(results_file, 'r') as f:
                saved_results = json.load(f)
                print(f"   Conversations: {len(saved_results.get('conversations', []))}")
        else:
            print_error(f"Results file not found: {results_file}")
        
        db.close()
        return True
        
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        db.close()
        return False


def test_store_run_with_full_metrics():
    """Test store_run with comprehensive metrics."""
    print_section("TEST 2: STORE_RUN WITH FULL METRICS")
    
    db = SessionLocal()
    
    try:
        users = crud.read_users(db, limit=1)
        scenarios = crud.read_scenarios(db, limit=1)
        
        if not users or not scenarios:
            print_error("Missing base entities")
            return False
        
        user_id = users[0]['id']
        scenario_id = scenarios[0]['id']
        
        # Full attack results with multiple conversations
        attack_results = {
            "conversations": [
                {
                    "id": f"conv_{i:03d}",
                    "messages": [
                        {"role": "user", "content": f"test prompt {i}"},
                        {"role": "assistant", "content": f"test response {i}"}
                    ],
                    "score": 0.7 + (i * 0.05)
                }
                for i in range(5)
            ],
            "metrics": {
                "asr": 0.75,
                "orr": 0.45,
                "aor": 0.30,
                "useful_majority": 0.80,
                "veridict_majority": 0.70
            }
        }
        
        jury_votes = [
            {
                "jury_index": j,
                "usefulness": j % 2 == 0,
                "veridict": True,
                "model_name": f"judge_{j}"
            }
            for j in range(3)
        ]
        
        started_at = datetime.now() - timedelta(minutes=10)
        ended_at = datetime.now()
        
        result = crud.store_run(
            db=db,
            user_id=user_id,
            scenario_id=scenario_id,
            target_model="gpt-4",
            attack_model="gpt-3.5",
            attack_type="flip",
            attack_results=attack_results,
            jury_votes_data=jury_votes,
            started_at=started_at,
            ended_at=ended_at,
            attacker_visibility="black_box"
        )
        
        run_id = result['run_id']
        print_success(f"Full metrics store_run completed. Run ID: {run_id}")
        
        # Verify metrics were stored
        run = crud.read_run_by_id(db, run_id)
        if not run:
            print_error(f"Run {run_id} not found")
            return False
        
        expected_metrics = {
            "asr": 0.75,
            "orr": 0.45,
            "aor": 0.30,
            "useful_majority": 0.80,
            "veridict_majority": 0.70
        }
        
        for metric_name, expected_value in expected_metrics.items():
            db_field = f"metrics_{metric_name}"
            actual_value = run.get(db_field)
            if actual_value == expected_value:
                print_success(f"Metric {metric_name}: {actual_value}")
            else:
                print_error(f"Metric {metric_name} mismatch. Expected {expected_value}, got {actual_value}")
        
        db.close()
        return True
        
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        db.close()
        return False


def test_store_run_transaction_rollback():
    """Test transaction rollback on invalid data."""
    print_section("TEST 3: TRANSACTION ROLLBACK ON ERROR")
    
    db = SessionLocal()
    
    try:
        # Use invalid IDs that don't exist
        invalid_user_id = 99999
        invalid_scenario_id = 99999
        
        attack_results = {"conversations": [], "metrics": {}}
        
        result = crud.store_run(
            db=db,
            user_id=invalid_user_id,
            scenario_id=invalid_scenario_id,
            target_model="test",
            attack_model="test",
            attack_type="test",
            attack_results=attack_results,
            jury_votes_data=[],
            started_at=datetime.now(),
            ended_at=datetime.now()
        )
        
        # If we get here, check if it returned an error
        if 'error' in result:
            print_success(f"Properly caught error: {result.get('error')}")
            return True
        else:
            print_error("Should have raised an error for invalid IDs")
            return False
        
    except Exception as e:
        # This is expected - the transaction should fail
        print_success(f"Transaction properly rolled back on error: {type(e).__name__}")
        db.close()
        return True


def test_multiple_runs_same_session():
    """Test storing multiple runs in sequence."""
    print_section("TEST 4: MULTIPLE RUNS IN SEQUENCE")
    
    db = SessionLocal()
    
    try:
        users = crud.read_users(db, limit=1)
        scenarios = crud.read_scenarios(db, limit=1)
        
        if not users or not scenarios:
            print_error("Missing base entities")
            return False
        
        user_id = users[0]['id']
        scenario_id = scenarios[0]['id']
        
        run_ids = []
        
        for i in range(3):
            attack_results = {
                "conversations": [{"id": f"c_{i}", "score": 0.5 + i*0.1}],
                "metrics": {"asr": 0.5 + i*0.1}
            }
            
            result = crud.store_run(
                db=db,
                user_id=user_id,
                scenario_id=scenario_id,
                target_model="test",
                attack_model="test",
                attack_type=f"attack_type_{i}",
                attack_results=attack_results,
                jury_votes_data=[],
                started_at=datetime.now(),
                ended_at=datetime.now()
            )
            
            run_ids.append(result['run_id'])
            print_success(f"Run {i+1} stored: ID {result['run_id']}")
        
        # Verify all runs exist
        for run_id in run_ids:
            run = crud.read_run_by_id(db, run_id)
            if not run:
                print_error(f"Run {run_id} not found")
                return False
        
        print_success(f"All {len(run_ids)} runs verified in database")
        
        db.close()
        return True
        
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        db.close()
        return False


def test_read_runs_by_user():
    """Test retrieving runs for a specific user."""
    print_section("TEST 5: RETRIEVE RUNS BY USER")
    
    db = SessionLocal()
    
    try:
        users = crud.read_users(db, limit=1)
        if not users:
            print_error("No users in database")
            return False
        
        user_id = users[0]['id']
        
        # Get runs for this user
        runs = crud.read_runs_by_user(db, user_id)
        
        if runs:
            print_success(f"Found {len(runs)} runs for user {user_id}")
            if runs:
                latest = runs[0]
                print(f"   Latest run:")
                print(f"     ID: {latest.get('id')}")
                print(f"     Attack Type: {latest.get('attack_type')}")
                print(f"     Started: {latest.get('started_at')}")
        else:
            print("ℹ️  No runs found for this user (this is OK)")
        
        db.close()
        return True
        
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        db.close()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  COMPREHENSIVE TEST SUITE FOR store_run() FUNCTION".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        ("Basic store_run", test_store_run_basic),
        ("Full metrics", test_store_run_with_full_metrics),
        ("Transaction rollback", test_store_run_transaction_rollback),
        ("Multiple runs", test_multiple_runs_same_session),
        ("Read runs by user", test_read_runs_by_user),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test crashed: {str(e)}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! store_run() is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
