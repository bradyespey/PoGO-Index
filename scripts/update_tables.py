# scripts/update_tables.py

import os
import sys
import subprocess
from pathlib import Path

# Define paths to SQLite scripts
sqlite_scripts = [
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_costumes.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_forms.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_poke_genie.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_pokemon.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_rocket.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_shinies.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_specials.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_all_pokemon.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_users.py"
]

# Define commands for PostgreSQL scripts to run on Heroku
postgres_commands = [
    "heroku run python /app/scripts/update_costumes.py --app pogo",
    "heroku run python /app/scripts/update_forms.py --app pogo",
    "heroku run python /app/scripts/update_poke_genie.py --app pogo",
    "heroku run python /app/scripts/update_pokemon.py --app pogo",
    "heroku run python /app/scripts/update_rocket.py --app pogo",
    "heroku run python /app/scripts/update_shinies.py --app pogo",
    "heroku run python /app/scripts/update_specials.py --app pogo",
    "heroku run python /app/scripts/update_all_pokemon.py --app pogo",
    "heroku run python /app/scripts/update_users.py --app pogo"
]

# Mapping of choices for individual scripts
sqlite_choices = {i + 3: script for i, script in enumerate(sqlite_scripts)}
postgres_choices = {i + 12: command for i, command in enumerate(postgres_commands)}

def run_script(script_path):
    """Run a Python script for SQLite updates."""
    print(f"Running {script_path}...")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

def run_heroku_command(command):
    """Run a Heroku command for PostgreSQL updates."""
    print(f"Running {command}...")
    process = subprocess.Popen(command, shell=True)
    process.communicate()  # This will wait for the process to finish

def update_all_sqlite():
    """Run all SQLite update scripts in sequence."""
    print("Updating all SQLite tables...")
    for script in sqlite_scripts:
        run_script(script)

def update_all_postgres():
    """Run all PostgreSQL update commands on Heroku in sequence."""
    print("Updating all PostgreSQL tables on Heroku...")
    for command in postgres_commands:
        run_heroku_command(command)

def update_selected_table(choice):
    """Run a specific SQLite or PostgreSQL update based on user selection."""
    if choice in sqlite_choices:
        run_script(sqlite_choices[choice])
    elif choice in postgres_choices:
        run_heroku_command(postgres_choices[choice])
    else:
        print("Invalid choice.")

def main():
    while True:
        print("\nSelect tables to update:")
        print("1. Update all SQLite tables")
        print("2. Update all PostgreSQL tables")
        
        print("\nSQLite tables:")
        for idx, script in sqlite_choices.items():
            table_name = Path(script).stem.replace("update_", "")
            print(f"{idx}. {table_name}")

        print("\nPostgreSQL tables:")
        for idx, command in postgres_choices.items():
            table_name = command.split()[3].replace("update_", "")
            print(f"{idx}. {table_name}")

        print("\n0. Cancel")

        try:
            choice = int(input("\nEnter your choice (1 to update all, number to update specific table, or 0 to cancel): "))
            if choice == 0:
                print("Operation cancelled.")
                return
            elif choice == 1:
                update_all_sqlite()
            elif choice == 2:
                update_all_postgres()
            elif choice in sqlite_choices or choice in postgres_choices:
                update_selected_table(choice)
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
