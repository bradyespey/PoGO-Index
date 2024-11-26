# scripts/list_column_tables.py

import os
import sys
from pathlib import Path
from sqlalchemy import inspect
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
        print("No database found. Please ensure the database is set up correctly.")
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

def show_columns(table_name):
    """Display all columns of a specific table."""
    inspector = inspect(db.engine)
    columns = inspector.get_columns(table_name)
    
    if columns:
        print(f"\nColumns in table '{table_name}':")
        for column in columns:
            print(f"  - {column['name']} (Type: {column['type']})")
    else:
        print(f"No columns found for table '{table_name}'.")

def show_all_columns(tables):
    """Display all columns for all tables."""
    for table in tables:
        show_columns(table)

def prompt_for_table(tables):
    """Prompt the user to select a table to view its columns."""
    while True:
        print("\nSelect a table to view its columns:")
        print("1. Show columns for all tables")
        for idx, table in enumerate(tables, start=2):
            print(f"{idx}. {table}")
        print("0. Cancel")

        try:
            choice = int(input("Enter your choice (1 to show all, number to show specific table, or 0 to cancel): "))
            if choice == 0:
                print("Operation cancelled.")
                return
            elif choice == 1:
                show_all_columns(tables)
                return
            elif 2 <= choice <= len(tables) + 1:
                show_columns(tables[choice - 2])
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    """Main function to manage the script."""
    with app.app_context():
        # Check if the database exists
        tables = check_db_exists()
        if not tables:
            print("No tables found in the database.")
            return

        # List tables and prompt for column inspection
        tables = list_tables()
        if tables:
            prompt_for_table(tables)

if __name__ == "__main__":
    main()