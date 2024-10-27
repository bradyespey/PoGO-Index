import os
import sys
from pathlib import Path
from sqlalchemy import inspect
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Importing the app and db for database management
from app import app, db

def check_db_exists():
    """Check if the database exists by trying to connect and inspect the tables."""
    try:
        # Reflect the current database tables
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if tables:
            print(f"Database found with {len(tables)} tables.")
        else:
            print("Database exists but has no tables.")
        return tables
    except OperationalError:
        print("No database found. Creating a new one.")
        return []

def list_tables():
    """List all tables in the database."""
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
    """Drop a specific table."""
    with app.app_context():
        print(f"Dropping table '{table_name}'...")
        db.session.execute(text(f'DROP TABLE IF EXISTS {table_name} CASCADE;'))
        db.session.commit()
        print(f"Table '{table_name}' dropped.")

def drop_all_tables(tables):
    """Drop all tables in the database."""
    with app.app_context():
        for table in tables:
            drop_table(table)
        print("All tables have been dropped.")

def drop_selected_tables(tables):
    """Prompt user to select tables to drop."""
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
                drop_all_tables(tables)
                return
            elif 2 <= choice <= len(tables) + 1:
                drop_table(tables[choice - 2])
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    """Main function to manage the drop script."""
    with app.app_context():
        # Check if the database exists or needs to be created
        tables = check_db_exists()
        if not tables:
            print("No tables to drop.")
            return

        # List the tables and prompt the user to drop
        tables = list_tables()
        if tables:
            drop_selected_tables(tables)
        else:
            print("No tables to drop.")

if __name__ == "__main__":
    main()
