import sys
from pathlib import Path
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app import app, db

def check_db_exists():
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if tables:
            print(f"Database found with {len(tables)} tables.")
        else:
            print("Database exists but has no tables.")
        return tables
    except OperationalError:
        print("No database found.")
        return []

def list_tables():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    if not tables:
        print("No tables found in the database.")
        return []
    
    print("Existing tables:")
    for idx, table in enumerate(tables, start=1):
        print(f"{idx}. {table}")
    
    return tables

def drop_table(table_name):
    with app.app_context():
        # Detect the current database dialect (SQLite vs PostgreSQL)
        dialect_name = db.engine.dialect.name

        print(f"Dropping table '{table_name}'...")

        if dialect_name == 'sqlite':
            # SQLite does not support CASCADE
            db.session.execute(text(f'DROP TABLE IF EXISTS "{table_name}";'))
        else:
            # For PostgreSQL, use CASCADE to drop dependent objects
            db.session.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;'))

        db.session.commit()
        print(f"Table '{table_name}' dropped.")

def drop_selected_tables(tables):
    while True:
        print("\nSelect tables to drop:")
        print("1. Drop all tables")
        for idx, table in enumerate(tables, start=2):
            print(f"{idx}. {table}")
        print("0. Cancel")

        try:
            choice = int(input("Enter your choice (1 to drop all, number to drop specific table, or 0 to cancel): "))
            if choice == 0:
                print("Operation cancelled.")
                return
            elif choice == 1:
                for table in tables:
                    drop_table(table)
                print("All tables have been dropped.")
                return
            elif 2 <= choice <= len(tables) + 1:
                drop_table(tables[choice - 2])
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    with app.app_context():
        tables = check_db_exists()
        if not tables:
            print("No tables to drop.")
            return

        tables = list_tables()
        if tables:
            drop_selected_tables(tables)
        else:
            print("No tables to drop.")

if __name__ == "__main__":
    main()