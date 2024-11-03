import os
import subprocess

# Define paths to local scripts and Heroku commands
local_scripts = [
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_users.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_costumes.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_forms.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_poke_genie.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_pokemon.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_rocket.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_shinies.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_specials.py",
    "/Users/bradyespey/Projects/GitHub/PoGO/scripts/update_all_pokemon.py",
]

heroku_commands = [
    "heroku run python /app/scripts/update_users.py --app pogo",
    "heroku run python /app/scripts/update_costumes.py --app pogo",
    "heroku run python /app/scripts/update_forms.py --app pogo",
    "heroku run python /app/scripts/update_poke_genie.py --app pogo",
    "heroku run python /app/scripts/update_pokemon.py --app pogo",
    "heroku run python /app/scripts/update_rocket.py --app pogo",
    "heroku run python /app/scripts/update_shinies.py --app pogo",
    "heroku run python /app/scripts/update_specials.py --app pogo",
    "heroku run python /app/scripts/update_all_pokemon.py --app pogo",
]

# Function to execute a command and capture any errors
def run_command(command, source=""):
    try:
        print(f"\nRunning: {command}")
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error in {source}: {e}")
        return str(e)
    return None

def main():
    # Prompt user for choice
    choice = input("Choose an option:\nL - Run local update scripts\nH - Run Heroku update scripts\nB - Run both update scripts\nEnter choice: ").upper()
    errors = []

    # Run local scripts
    if choice in ["L", "B"]:
        print("\n--- Running Local Scripts ---")
        for script in local_scripts:
            error = run_command(f"python {script}", source=f"Local script {script}")
            if error:
                errors.append(error)

    # Run Heroku scripts
    if choice in ["H", "B"]:
        print("\n--- Running Heroku Scripts ---")
        for command in heroku_commands:
            error = run_command(command, source=f"Heroku command {command}")
            if error:
                errors.append(error)

    # Display errors at the end, if any
    if errors:
        print("\n--- Errors Summary ---")
        for err in errors:
            print(err)
    else:
        print("\nAll scripts ran successfully.")

if __name__ == "__main__":
    main()
