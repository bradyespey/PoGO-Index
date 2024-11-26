# scripts/reset_tables.py

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

from sqlalchemy import text

def reset_table(table_name):
    """Drop and recreate a specific table."""
    with app.app_context():
        # Detect the current database dialect (SQLite vs PostgreSQL)
        dialect_name = db.engine.dialect.name

        print(f"Dropping table '{table_name}'...")

        if dialect_name == 'sqlite':
            # SQLite does not support CASCADE
            db.session.execute(text(f'DROP TABLE IF EXISTS {table_name};'))
        else:
            # For PostgreSQL, use CASCADE to drop dependent objects
            db.session.execute(text(f'DROP TABLE IF EXISTS {table_name} CASCADE;'))

        db.session.commit()

        print(f"Recreating table '{table_name}'...")
        db.create_all()
        db.session.commit()

def reset_selected_tables(tables):
    """Prompt user to select tables to reset."""
    while True:
        print("\nSelect tables to reset:")
        print("1. Reset all tables")
        for idx, table in enumerate(tables, start=2):
            print(f"{idx}. {table}")
        print("0. Cancel")

        try:
            choice = int(input("Enter your choice (1 to reset all, number to reset specific table, or 0 to cancel): "))
            if choice == 0:
                print("Operation cancelled.")
                return
            elif choice == 1:
                reset_all_tables(tables)
                return
            elif 2 <= choice <= len(tables) + 1:
                reset_table(tables[choice - 2])
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def reset_all_tables(tables):
    """Reset all tables in the database."""
    for table in tables:
        reset_table(table)

def main():
    """Main function to manage the reset script."""
    with app.app_context():
        # Check if the database exists or needs to be created
        tables = check_db_exists()
        if not tables:
            # If no tables found, create the database and exit
            print("Creating the database with all tables...")
            db.create_all()
            print("Database created successfully.")
            return

        # List the tables and prompt the user to reset
        tables = list_tables()
        if tables:
            reset_selected_tables(tables)
        else:
            print("No tables to reset.")

if __name__ == "__main__":
    main()