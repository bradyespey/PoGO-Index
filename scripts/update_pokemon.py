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
from models import Pokemon, PokeGenieEntry

# Specific forms to skip
FORMS_TO_SKIP = [" Mega ", " Alolan ", " Galarian ", " Hisuian "]

def fetch_pokemon_data():
    print("Fetching and updating Pokémon data...")

    # Scrape Pokémon data
    url = "https://pokemondb.net/go/pokedex"
    start_time = time.time()
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find("table", {"id": "pokedex"})
    rows = table.find_all("tr")[1:]  # Skip the header row

    # Define image directory paths (local for dev)
    local_image_dir = '/Users/bradyespey/Projects/GitHub/PoGO/static/images/mons'
    relative_image_url_base = '/static/images/mons'

    count_inserted, count_updated, count_skipped, count_with_images = 0, 0, 0, 0

    for idx, row in enumerate(rows):
        cols = row.find_all("td")
        dex_number = int(cols[0].text.strip())
        name = cols[1].text.strip().replace("♀", "-f").replace("♂", "-m")
        type_ = " ".join([t.text for t in cols[2].find_all("a")])

        # Skip unwanted forms
        if any(form in name for form in FORMS_TO_SKIP):
            continue

        # Construct image filename
        image_filename = f"{name.lower().replace(' ', '-').replace(':', '')}.png"
        local_image_path = os.path.join(local_image_dir, image_filename)
        relative_image_url = f"{relative_image_url_base}/{image_filename}"

        image_url_to_store = relative_image_url if os.path.exists(local_image_path) else None

        # Check if Pokémon already exists in the database
        pokemon = Pokemon.query.filter_by(id=dex_number).first()

        if pokemon:
            # Update if necessary
            if pokemon.image_url != image_url_to_store:
                pokemon.image_url = image_url_to_store
                db.session.commit()
                count_updated += 1
            else:
                count_skipped += 1
        else:
            # Add new Pokémon with user-specific columns defaulted to 0 for Matt and Brady, 1 for iPad
            new_pokemon = Pokemon(
                id=dex_number,
                name=name,
                type=type_,
                image_url=image_url_to_store,
                user_1_living_dex=False,  # Default to 0 for Brady
                user_1_lucky=False,
                user_2_living_dex=False,  # Default to 0 for Matt
                user_2_lucky=False,
                user_0_living_dex=True,   # Default to 1 for iPad
                user_0_lucky=False,       # Default to 0 for iPad
            )
            db.session.add(new_pokemon)
            db.session.commit()
            count_inserted += 1

        # Logic for Brady's data from PokeGenie (for each dex_number)
        poke_genie_entries = PokeGenieEntry.query.filter_by(pokemon_number=dex_number).all()

        for poke_genie_entry in poke_genie_entries:
            # Brady's Living Dex logic (user_1_living_dex)
            if (
                poke_genie_entry.lucky == 0 and
                poke_genie_entry.shadow_purified == 0 and
                poke_genie_entry.favorite == 0
            ):
                pokemon.user_1_living_dex = True

            # Brady's Lucky Dex logic (user_1_lucky)
            if (
                poke_genie_entry.lucky == 1 and
                poke_genie_entry.shadow_purified == 0 and
                poke_genie_entry.favorite == 0
            ):
                pokemon.user_1_lucky = True

            # iPad Living Dex logic (user_0_living_dex)
            if (
                poke_genie_entry.lucky == 0 and
                poke_genie_entry.shadow_purified == 0 and
                poke_genie_entry.favorite == 4
            ):
                pokemon.user_0_living_dex = False  # Mark as "No" for iPad

            db.session.commit()

        # Log progress every 10 entries
        if idx % 10 == 0:
            print(f"Processing Pokémon {idx + 1}/{len(rows)}...")

    print(f"Finished processing {len(rows)} Pokémon.")
    print(f"Total Pokémon added: {count_inserted}")
    print(f"Total Pokémon updated: {count_updated}")
    print(f"Total Pokémon skipped: {count_skipped}")
    print(f"Total Pokémon with images: {count_with_images}")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        fetch_pokemon_data()