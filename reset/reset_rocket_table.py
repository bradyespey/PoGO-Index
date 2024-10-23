import os
import sys
from pathlib import Path
import subprocess

# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Now we import app and db inside the functions to avoid any circular import issues
def drop_rocket_table():
    """Drop the 'rocket' table from the PostgreSQL database."""
    from app import app, db  # Import app and db locally
    with app.app_context():
        db.drop_all()  # Drop all tables including 'rocket'
        db.session.commit()
        print("Dropped all tables.")

def recreate_rocket_table():
    """Recreate the 'rocket' table using SQLAlchemy."""
    from app import app, db  # Import app and db locally
    with app.app_context():
        db.create_all()  # Recreate all tables, including the updated 'rocket' table
        db.session.commit()
        print("Recreated all tables.")

def run_flask_migrations():
    """Run the Flask migration commands."""
    try:
        project_root = Path(__file__).resolve().parent.parent  # Set project root directory
        os.chdir(project_root)  # Change to the project directory

        # Ensure FLASK_APP environment variable is set
        os.environ['FLASK_APP'] = "app.py"

        print("Running flask db migrate...")
        subprocess.run(["flask", "db", "migrate"], check=True)
        print("Running flask db upgrade...")
        subprocess.run(["flask", "db", "upgrade"], check=True)
        print("Flask migrations applied successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during migrations: {e}")
        sys.exit(1)

def run_update_script():
    """Run the update script for the 'rocket' table."""
    try:
        print("Running update_rocket.py script...")
        update_script_path = Path(__file__).resolve().parent.parent / 'update' / 'update_rocket.py'
        subprocess.run([sys.executable, str(update_script_path)], check=True)
        print("Update script ran successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error while running the update script: {e}")
        sys.exit(1)

def main():
    # Drop the existing 'rocket' table
    drop_rocket_table()

    # Recreate the 'rocket' table with the new fields
    recreate_rocket_table()

    # Run Flask migration commands
    run_flask_migrations()

    # Run the update script
    run_update_script()

if __name__ == "__main__":
    main()
