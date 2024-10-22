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
from models import Rocket

def fetch_rocket_pokemon_data(app_context):
    with app_context:
        print("Fetching and updating Team Rocket Pokémon data...")

        url = "https://www.serebii.net/pokemongo/shadowpokemon.shtml"
        start_time = time.time()
        print(f"Fetching data from {url}...")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Fetched data in {time.time() - start_time:.2f} seconds")

        # Parse the HTML table
        table = soup.find_all("table")[1]
        rows = table.find_all("tr")[1:]  # Skip the header row
        total_rockets = len(rows)
        print(f"Found {total_rockets} Team Rocket Pokémon in the data.")

        count_inserted, count_updated, count_skipped = 0, 0, 0

        # Process each Team Rocket Pokémon
        for idx, row in enumerate(rows):
            cols = row.find_all("td", recursive=False)

            if len(cols) < 4:
                continue

            dex_number = int(cols[0].get_text(strip=True).replace('#', ''))
            name = cols[2].get_text(strip=True)
            method = cols[4].get_text(strip=True)

            # Check if the Rocket entry already exists
            rocket_pokemon = Rocket.query.filter(Rocket.dex_number == dex_number, Rocket.name == name).first()

            if rocket_pokemon:
                if rocket_pokemon.method != method:
                    rocket_pokemon.method = method
                    db.session.commit()
                    count_updated += 1
                else:
                    count_skipped += 1
            else:
                new_rocket = Rocket(dex_number=dex_number, name=name, method=method)
                db.session.add(new_rocket)
                db.session.commit()
                count_inserted += 1

            # Log progress
            if idx % 10 == 0:
                print(f"Processing Team Rocket Pokémon {idx + 1}/{total_rockets}...")

        # Final output
        print(f"Finished processing {total_rockets} Team Rocket Pokémon.")
        print(f"Total Rocket Pokémon added: {count_inserted}")
        print(f"Total Rocket Pokémon updated: {count_updated}")
        print(f"Total Rocket Pokémon skipped: {count_skipped}")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        fetch_rocket_pokemon_data(app.app_context())