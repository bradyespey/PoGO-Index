import os
import sys
from pathlib import Path
import subprocess

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

def drop_specials_table():
    """Drop the 'specials' table."""
    from app import app, db
    with app.app_context():
        db.drop_all()
        db.session.commit()
        print("Dropped all tables.")

def recreate_specials_table():
    """Recreate the 'specials' table using SQLAlchemy."""
    from app import app, db
    with app.app_context():
        db.create_all()
        db.session.commit()
        print("Recreated all tables.")

def run_update_script():
    """Run the update script for the 'specials' table."""
    try:
        update_script_path = Path(__file__).resolve().parent / 'update_specials.py'
        subprocess.run([sys.executable, str(update_script_path)], check=True)
        print("Update script ran successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error while running the update script: {e}")
        sys.exit(1)

def main():
    drop_specials_table()
    recreate_specials_table()
    run_update_script()

if __name__ == "__main__":
    main()