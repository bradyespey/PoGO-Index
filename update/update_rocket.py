import requests
from bs4 import BeautifulSoup
import sqlite3

# Path to your SQLite database
db_path = "C:/Projects/GitHub/PoGO/pogo.db"

def sanitize_string(value):
    """Remove or replace special characters that cause encoding issues."""
    if value:
        return value.encode('ascii', 'ignore').decode()
    return None

def fetch_rocket_pokemon_data():
    """Fetch Team Rocket Pokémon data from Serebii and update the SQLite database."""
    url = "https://www.serebii.net/pokemongo/shadowpokemon.shtml"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the second table on the page (List of Available Shadow Pokémon)
    table = soup.find_all("table")[1]
    rows = table.find_all("tr")[1:]  # Skip the header row

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    count_updated = 0
    count_inserted = 0
    total_pokemon = len(rows)

    # Process the rows and count updates and inserts
    for row in rows:
        cols = row.find_all("td", recursive=False)

        # Skip rows that do not contain enough columns
        if len(cols) < 4:
            continue

        # Extract relevant data
        dex_number_raw = cols[0].get_text(strip=True)  # Dex Number
        dex_number = int(dex_number_raw.replace('#', ''))  # Strip '#' and convert to integer
        name = sanitize_string(cols[2].get_text(strip=True))  # Name
        method = sanitize_string(cols[4].get_text(strip=True))  # Stats (we'll call this 'method' in DB)

        # Check if the Pokémon entry already exists
        cursor.execute("SELECT * FROM rocket WHERE dex_number = ? AND name = ?", (dex_number, name))
        existing_entry = cursor.fetchone()

        if existing_entry:
            # Update the existing entry
            cursor.execute('''
                UPDATE rocket
                SET method = ?
                WHERE dex_number = ? AND name = ?
            ''', (method, dex_number, name))
            count_updated += 1
        else:
            # Insert a new entry
            cursor.execute('''
                INSERT INTO rocket (dex_number, name, method)
                VALUES (?, ?, ?)
            ''', (dex_number, name, method))
            count_inserted += 1

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Summary output
    print(f"Finished fetching and saving Rocket Pokémon data.")
    print(f"Total Rocket Pokémon processed: {total_pokemon}")
    print(f"Total Rocket Pokémon added: {count_inserted}")
    print(f"Total Rocket Pokémon updated: {count_updated}")

if __name__ == "__main__":
    fetch_rocket_pokemon_data()