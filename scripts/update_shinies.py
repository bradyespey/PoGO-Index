import os
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time

# Add the project root directory to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Now, you can import app and models after sys.path is correctly set
from app import app, db
from models import ShinyPokemon

def fetch_shiny_pokemon_data(app_context):
    with app_context:
        print("Fetching and updating Shiny Pokémon data...")

        url = "https://www.serebii.net/pokemongo/shiny.shtml"
        start_time = time.time()
        print(f"Fetching data from {url}...")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Fetched data in {time.time() - start_time:.2f} seconds")

        # Parse the HTML table
        table = soup.find_all("table")[1]
        rows = table.find_all("tr")[1:]  # Skip the header row
        total_shinies = len(rows)
        print(f"Found {total_shinies} Shiny Pokémon in the data.")

        count_inserted, count_updated, count_skipped = 0, 0, 0

        # Process each Shiny Pokémon
        for idx, row in enumerate(rows):
            cols = row.find_all("td", recursive=False)

            if len(cols) < 5:
                continue

            dex_number = int(cols[0].get_text(strip=True).replace('#', ''))
            name = cols[2].get_text(strip=True)
            method = cols[4].get_text(strip=True)

            # Default user_id (replace this with actual user logic)
            user_id = 1  # Assign the appropriate user_id

            # Check if the Shiny entry already exists
            shiny_pokemon = ShinyPokemon.query.filter_by(dex_number=dex_number, name=name, user_id=user_id).first()

            if shiny_pokemon:
                if shiny_pokemon.method != method:
                    shiny_pokemon.method = method
                    db.session.commit()
                    count_updated += 1
                else:
                    count_skipped += 1
            else:
                # Insert new Shiny Pokémon
                new_shiny = ShinyPokemon(dex_number=dex_number, name=name, method=method, user_id=user_id)
                db.session.add(new_shiny)
                db.session.commit()
                count_inserted += 1

            # Log progress every 10 Pokémon
            if idx % 10 == 0:
                print(f"Processing Shiny Pokémon {idx + 1}/{total_shinies}...")

        # Final output
        print(f"Finished processing {total_shinies} Shiny Pokémon.")
        print(f"Total Shiny Pokémon added: {count_inserted}")
        print(f"Total Shiny Pokémon updated: {count_updated}")
        print(f"Total Shiny Pokémon skipped: {count_skipped}")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        fetch_shiny_pokemon_data(app.app_context())