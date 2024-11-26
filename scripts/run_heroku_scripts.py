# scripts/run_heroku_scripts.py

import os
import subprocess

# Path to your scripts folder
SCRIPTS_FOLDER = "/Users/bradyespey/Projects/GitHub/PoGO/scripts"
HEROKU_APP_NAME = "pogo"  # Your Heroku app name

def list_scripts(folder):
    """List all Python scripts in the given folder."""
    try:
        scripts = [f for f in os.listdir(folder) if f.endswith(".py")]
        if not scripts:
            print("No Python scripts found in the folder.")
        return scripts
    except FileNotFoundError:
        print(f"Folder not found: {folder}")
        return []

def prompt_for_script(scripts):
    """Prompt the user to select a script to run."""
    while True:
        print("\nAvailable scripts:")
        for idx, script in enumerate(scripts, start=1):
            print(f"{idx}. {script}")
        print("0. Cancel")

        try:
            choice = int(input("Enter the number of the script to run, or 0 to cancel: "))
            if choice == 0:
                print("Operation cancelled.")
                return None
            elif 1 <= choice <= len(scripts):
                return scripts[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def run_heroku_script(script_name):
    """Run the selected script on Heroku."""
    command = [
        "heroku", "run", "python", f"/app/scripts/{script_name}",
        "--app", HEROKU_APP_NAME
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script_name}: {e}")

def main():
    """Main function to list, select, and run a Heroku script."""
    scripts = list_scripts(SCRIPTS_FOLDER)
    if not scripts:
        return

    script_to_run = prompt_for_script(scripts)
    if script_to_run:
        print(f"Running {script_to_run} on Heroku...")
        run_heroku_script(script_to_run)

if __name__ == "__main__":
    main()