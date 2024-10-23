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
from models import Pokemon

# Specific forms to skip
FORMS_TO_SKIP = [" Mega ", " Alolan ", " Galarian ", " Hisuian "]

def fetch_pokemon_data(app_context):
    with app_context:
        print("Fetching and updating Pokémon data...")

        # Scrape Pokémon data
        url = "https://pokemondb.net/go/pokedex"
        start_time = time.time()
        print(f"Fetching data from {url}...")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Fetched data in {time.time() - start_time:.2f} seconds")

        # Parse HTML table
        table = soup.find("table", {"id": "pokedex"})
        rows = table.find_all("tr")[1:]  # Skip the header row
        total_pokemon = len(rows)
        print(f"Found {total_pokemon} Pokémon in the data.")

        # Define the image directory path (local for checking, relative for storing in DB)
        local_image_dir = '/Users/bradyespey/Projects/GitHub/PoGO/static/images/mons'  # Local path for dev
        relative_image_url_base = '/static/images/mons'  # Relative path to store in DB

        count_inserted, count_updated, count_skipped, count_with_images = 0, 0, 0, 0

        # Process each Pokémon
        for idx, row in enumerate(rows):
            cols = row.find_all("td")
            dex_number = int(cols[0].text.strip())  # Dex number as integer
            name = cols[1].text.strip().replace("♀", "-f").replace("♂", "-m")
            type_ = " ".join([t.text for t in cols[2].find_all("a")])  # Pokémon type

            # Skip unwanted forms
            if any(form in name for form in FORMS_TO_SKIP):
                continue

            # Construct image filename
            image_filename = f"{name.lower().replace(' ', '-').replace(':', '')}.png"
            local_image_path = os.path.join(local_image_dir, image_filename)
            relative_image_url = f"{relative_image_url_base}/{image_filename}"

            # Check if the image exists locally for dev
            image_url_to_store = relative_image_url if os.path.exists(local_image_path) else None

            if image_url_to_store:
                count_with_images += 1

            # Check if Pokémon already exists in the database
            pokemon = Pokemon.query.filter_by(id=dex_number).first()

            if pokemon:
                # Pokémon already exists, update image if needed
                if pokemon.image_url != image_url_to_store:
                    pokemon.image_url = image_url_to_store
                    db.session.commit()
                    count_updated += 1
                else:
                    count_skipped += 1
            else:
                # Insert new Pokémon entry
                new_pokemon = Pokemon(
                    id=dex_number,
                    name=name,
                    type=type_,
                    image_url=image_url_to_store,
                )
                db.session.add(new_pokemon)
                db.session.commit()
                count_inserted += 1

            # Log progress every 10 entries
            if idx % 10 == 0:
                print(f"Processing Pokémon {idx + 1}/{total_pokemon}...")

        print(f"Finished processing {total_pokemon} Pokémon.")
        print(f"Total Pokémon added: {count_inserted}")
        print(f"Total Pokémon updated: {count_updated}")
        print(f"Total Pokémon skipped: {count_skipped}")
        print(f"Total Pokémon with images: {count_with_images}")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        fetch_pokemon_data(app.app_context())