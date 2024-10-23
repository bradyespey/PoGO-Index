import os
import sys
from pathlib import Path

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Now we import app and db inside the functions to avoid any circular import issues
def drop_forms_table():
    """Drop the 'forms' table from the database."""
    from app import app, db  # Import app and db locally
    with app.app_context():
        db.drop_all()  # Drop all tables including 'forms'
        db.session.commit()
        print("Dropped all tables.")

def recreate_forms_table():
    """Recreate the 'forms' table using SQLAlchemy."""
    from app import app, db  # Import app and db locally
    with app.app_context():
        db.create_all()  # Recreate all tables, including the updated 'forms' table
        db.session.commit()
        print("Recreated all tables.")

def main():
    # Drop the existing 'forms' table
    drop_forms_table()

    # Recreate the 'forms' table with the new fields
    recreate_forms_table()

if __name__ == "__main__":
    main()