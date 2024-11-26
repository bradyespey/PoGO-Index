# scripts/check_db_entries.py

import os
import sys
from pathlib import Path
from sqlalchemy import inspect, Table, MetaData, select
from sqlalchemy.exc import OperationalError

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Importing the app and db for database management
from app import app, db

# User-defined variables
TABLE_TO_OUTPUT = 'all_pokemon'  # Set to 'all' or specific table name
NUM_ROWS_TO_OUTPUT = '10'  # Set to 'all' or integer number of rows as a string

def check_table_entries():
    with app.app_context():
        # Get the inspector for the database
        inspector = inspect(db.engine)
        all_tables = inspector.get_table_names()
        if not all_tables:
            print("No tables found in the database.")
            return

        print(f"Database found with {len(all_tables)} tables.")

        # Determine which tables to process
        if TABLE_TO_OUTPUT.lower() == 'all':
            tables_to_process = all_tables
        else:
            if TABLE_TO_OUTPUT in all_tables:
                tables_to_process = [TABLE_TO_OUTPUT]
            else:
                print(f"Table '{TABLE_TO_OUTPUT}' not found in the database.")
                return

        # Create a MetaData object for reflection
        metadata = MetaData()

        for table_name in tables_to_process:
            print(f"\nFirst {NUM_ROWS_TO_OUTPUT} rows for '{table_name}' table:")
            # Reflect the table
            try:
                table = Table(table_name, metadata, autoload_with=db.engine)
            except Exception as e:
                print(f"Error reflecting table '{table_name}': {e}")
                continue

            # Get column names
            columns = [str(column.name) for column in table.columns]
            # Print column headers in CSV format
            print(", ".join(columns))

            # Build a select query
            stmt = select(table)
            if NUM_ROWS_TO_OUTPUT.lower() != 'all':
                try:
                    limit = int(NUM_ROWS_TO_OUTPUT)
                    stmt = stmt.limit(limit)
                except ValueError:
                    print(f"Invalid number of rows: {NUM_ROWS_TO_OUTPUT}")
                    return

            # Execute the query
            try:
                result = db.session.execute(stmt)
                rows = result.fetchall()
                if not rows:
                    print("No entries found.")
                    continue

                # Print the rows
                for row in rows:
                    # Access row data using the mapping interface
                    row_mapping = row._mapping
                    row_data = [str(row_mapping.get(col, '')) for col in columns]
                    print(", ".join(row_data))
            except Exception as e:
                print(f"Error querying table '{table_name}': {e}")
                continue

if __name__ == "__main__":
    check_table_entries()
