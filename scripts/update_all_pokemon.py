# scripts/update_all_pokemon.py

import os
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
import re

# Add the project root directory to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import app and models after sys.path is correctly set
from app import app, db
from models import AllPokemon, Pokemon

# Mapping of superscript letters to categories
SUPERSCRIPT_MAP = {
    'S': 'Starter',
    'F': 'Fossil',
    'B': 'Baby',
    'L': 'Legendary',
    'M': 'Mythical',
    'U': 'Ultra Beast',
    'P': 'Paradox'
}

# Generation Ranges based on National Dex Number
GENERATION_RANGES = {
    1: range(1, 152),
    2: range(152, 252),
    3: range(252, 387),
    4: range(387, 494),
    5: range(494, 650),
    6: range(650, 722),
    7: range(722, 810),
    8: range(810, 906),
    9: range(906, 1025)
}

def get_generation(dex_number):
    for generation, dex_range in GENERATION_RANGES.items():
        if dex_number in dex_range:
            return generation
    return None

def fetch_all_pokemon_data():
    print("Fetching and updating All Pokémon data...")

    url = "https://en.wikipedia.org/wiki/List_of_Pok%C3%A9mon"
    start_time = time.time()
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"Fetched data from {url} in {time.time() - start_time:.2f} seconds")
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return

    # Find the table containing all Pokémon
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all("table", class_="wikitable")
    if len(tables) < 3:
        print("Error: Could not find the Pokémon table.")
        return

    pokemon_table = tables[2]  # Third table (index 2)
    print("Found the Pokémon table.")

    # Fetch all released dex numbers from the Pokémon Go table for released status check
    released_dex_numbers = {p.dex_number for p in Pokemon.query.with_entities(Pokemon.dex_number).all()}

    total_pokemon = 0
    count_inserted, count_updated, count_skipped = 0, 0, 0

    rows = pokemon_table.find_all("tr")
    # Skip the header row and process each Pokémon row
    for row_index, row in enumerate(rows[1:], start=1):
        cols = row.find_all("td")
        if not cols:
            continue  # Skip rows without columns

        num_columns = len(cols)
        num_pokemon_in_row = num_columns // 2

        # Iterate over each Pokémon in the row
        for idx in range(num_pokemon_in_row):
            dex_num_col = cols[idx * 2]
            name_col = cols[idx * 2 + 1]

            # Extract Dex Number
            dex_number_text = dex_num_col.get_text(strip=True).replace('#', '')
            try:
                dex_number = int(dex_number_text)
            except ValueError:
                continue

            # Extract Name and Superscripts
            name_cell = name_col
            name_link = name_cell.find('a')
            if name_link:
                name = name_link.text.strip()
                link = f"https://en.wikipedia.org{name_link['href']}"
            else:
                name = name_cell.get_text(strip=True)
                link = None

            # Check for superscripts (special categories)
            superscripts = name_cell.find_all('sup')
            categories = [SUPERSCRIPT_MAP.get(char, '') for sup in superscripts for char in sup.get_text() if char in SUPERSCRIPT_MAP]
            category = ", ".join(filter(None, categories))  # Join non-empty categories

            # Get generation based on dex number
            generation = get_generation(dex_number)

            # Check if this Pokémon is released in Pokémon Go
            released_in_pogo = dex_number in released_dex_numbers

            # Check if this Pokémon already exists in the AllPokemon table
            all_pokemon = AllPokemon.query.filter_by(dex_number=dex_number).first()
            if not all_pokemon:
                print(f"Inserting new Pokémon {name} with dex number {dex_number}.")
                all_pokemon = AllPokemon(
                    dex_number=dex_number,
                    name=name,
                    link=link,
                    category=category,
                    generation=generation,
                    released=released_in_pogo  # Set released status based on lookup
                )
                db.session.add(all_pokemon)
                count_inserted += 1
            else:
                # Update existing Pokémon if any data has changed
                updated = False
                if all_pokemon.name != name:
                    all_pokemon.name = name
                    updated = True
                if all_pokemon.link != link:
                    all_pokemon.link = link
                    updated = True
                if all_pokemon.category != category:
                    all_pokemon.category = category
                    updated = True
                if all_pokemon.generation != generation:
                    all_pokemon.generation = generation
                    updated = True
                if all_pokemon.released != released_in_pogo:
                    all_pokemon.released = released_in_pogo
                    updated = True
                if updated:
                    print(f"Updated Pokémon {name} with dex number {dex_number}.")
                    count_updated += 1
                else:
                    count_skipped += 1

            # Commit changes to the database
            db.session.commit()
            total_pokemon += 1

        # Log progress every 10 rows
        if row_index % 10 == 0:
            print(f"Processed row {row_index}... Total Pokémon processed so far: {total_pokemon}")

    print(f"Finished processing {total_pokemon} Pokémon.")
    print(f"Total Pokémon added: {count_inserted}")
    print(f"Total Pokémon updated: {count_updated}")
    print(f"Total Pokémon skipped: {count_skipped}")

if __name__ == "__main__":
    with app.app_context():
        fetch_all_pokemon_data()