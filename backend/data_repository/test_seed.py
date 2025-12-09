import sys
import os

# Add workspace root and backend to python path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import SessionLocal
from data_repository.crud import seed_database, read_all_from_table
from sqlalchemy import text

def run_seed_test():
    print("Starting database seed test...")
    
    db = SessionLocal()
    try:
        # Clean up existing data to avoid unique constraint errors if run multiple times
        # Order matters due to foreign keys
        print("Cleaning up existing data...")
        # Using CASCADE to handle foreign key dependencies
        # Note: TRUNCATE is faster than DELETE and resets identity columns (auto-increment)
        tables = ["jury_votes", "runs_metrics_models", "runs_metrics", "users_attack_loads", "users_workload_datasets", "scenarios_users", "workload_datasets", "attack_loads", "scenarios", "users", "models"]
        for table in tables:
            try:
                db.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
            except Exception as e:
                print(f"Warning: Could not truncate {table}: {e}")
        
        db.commit()
        
        print("Running seed_database()...")
        counts = seed_database(db)
        
        print("\nSeed results:")
        for table, count in counts.items():
            print(f"  {table}: {count}")
            
        # Verify data in tables
        print("\nVerifying data in tables:")
        tables_to_check = ["users", "scenarios", "workload_datasets", "attack_loads", "models", "runs_metrics", "jury_votes", "runs_metrics_models", "users_attack_loads", "users_workload_datasets", "scenarios_users"]
        
        all_good = True
        for table in tables_to_check:
            records = read_all_from_table(db, table)
            actual_count = len(records)
            expected_count = counts.get(table, 0)
            
            print(f"  Table '{table}': Found {actual_count} records (Expected {expected_count})")
            
            if actual_count != expected_count:
                print(f"    ERROR: Count mismatch for {table}!")
                all_good = False
            else:
                if actual_count > 0:
                    # Print a simplified version of the first record to avoid clutter
                    sample = records[0]
                    simple_sample = {k: v for k, v in sample.items() if k in ['id', 'name', 'email', 'target_model']}
                    print(f"    Sample record: {simple_sample}")
        
        if all_good:
            print("\nSUCCESS: Database seeded and verified correctly!")
        else:
            print("\nFAILURE: Some tables were not populated correctly.")
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seed_test()
