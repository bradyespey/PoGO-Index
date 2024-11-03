import os
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time

# Add the project root directory to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import app and models after sys.path is correctly set
from app import app, db
from models import Pokemon, PokeGenieEntry

# Specific forms to skip
FORMS_TO_SKIP = [" Mega ", " Alolan ", " Galarian ", " Hisuian "]

def fetch_pokemon_data():
    print("Fetching and updating Pokémon data...")

    # Scrape Pokémon data
    url = "https://pokemondb.net/go/pokedex"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        print("Data fetched from Pokémon DB website successfully.")
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find("table", {"id": "pokedex"})
    
    if not table:
        print("Pokedex table not found on the page.")
        return
    
    rows = table.find_all("tr")[1:]  # Skip the header row
    print(f"Found {len(rows)} Pokémon entries.")

    local_image_dir = '/Users/bradyespey/Projects/GitHub/PoGO/static/images/mons'
    relative_image_url_base = '/static/images/mons'
    os.makedirs(local_image_dir, exist_ok=True)  # Ensure image directory exists

    count_inserted, count_updated, count_skipped, count_with_images = 0, 0, 0, 0

    for row in rows:
        cols = row.find_all("td")
        dex_number = int(cols[0].text.strip())
        name = cols[1].text.strip().replace("♀", "-f").replace("♂", "-m")
        type_ = " ".join([t.text for t in cols[2].find_all("a")])

        # Skip unwanted forms
        if any(form in name for form in FORMS_TO_SKIP):
            print(f"Skipping form {name}")
            continue

        # Construct image filename and paths
        image_filename = f"{name.lower().replace(' ', '-').replace(':', '')}.png"
        local_image_path = os.path.join(local_image_dir, image_filename)
        relative_image_url = f"{relative_image_url_base}/{image_filename}"
        
        # Download image if it doesn't exist
        if not os.path.exists(local_image_path):
            image_url = f"https://img.pokemondb.net/sprites/go/normal/{image_filename}"
            try:
                img_data = requests.get(image_url).content
                with open(local_image_path, 'wb') as img_file:
                    img_file.write(img_data)
                print(f"Downloaded image for {name}")
                count_with_images += 1
            except requests.RequestException:
                print(f"Failed to download image for {name}")
        
        # Update database with image URL
        image_url_to_store = relative_image_url if os.path.exists(local_image_path) else None
        # Fetch or create Pokémon entry in the database
        pokemon = Pokemon.query.filter_by(dex_number=dex_number).first()
        if not pokemon:
            print(f"Inserting new Pokémon {name} with dex number {dex_number}")
            pokemon = Pokemon(
                dex_number=dex_number,
                name=name,
                type=type_,
                image_url=image_url_to_store,
                user_1_living_dex=False,
                user_1_lucky=False,
                user_2_living_dex=False,
                user_2_lucky=False,
                user_0_living_dex=True,
                user_0_lucky=False
            )
            db.session.add(pokemon)
            count_inserted += 1
        else:
            # Update image URL if it has changed
            if pokemon.image_url != image_url_to_store:
                pokemon.image_url = image_url_to_store
                count_updated += 1
            else:
                count_skipped += 1

        # Default fields as specified
        pokemon.user_1_living_dex = False
        pokemon.user_1_lucky = False
        pokemon.user_0_living_dex = True

        # Fetch PokeGenie entries for this Pokémon
        poke_genie_entries = PokeGenieEntry.query.filter_by(pokemon_number=dex_number).all()

        # Process each entry and update flags based on the specified logic
        for entry in poke_genie_entries:
            if not pokemon:
                print(f"Error: Pokémon with dex number {dex_number} not found.")
                continue

            # Brady's Living Dex logic
            if entry.lucky == 0 and entry.shadow_purified == 0 and (entry.favorite == 0 or entry.favorite == 4):
                pokemon.user_1_living_dex = True

            # Brady's Lucky Dex logic
            if entry.lucky == 1 and entry.shadow_purified == 0 and entry.favorite == 0:
                pokemon.user_1_lucky = True

            # iPad's Living Dex logic
            if entry.lucky == 0 and entry.shadow_purified == 0 and entry.favorite == 4:
                pokemon.user_0_living_dex = False

        # Commit changes for each Pokémon to the database
        db.session.commit()

    # Final output
    print(f"Finished processing {len(rows)} Pokémon")
    print(f"Total Pokémon added: {count_inserted}")
    print(f"Total Pokémon updated: {count_updated}")
    print(f"Total Pokémon skipped: {count_skipped}")
    print(f"Total Pokémon with images: {count_with_images}")

if __name__ == "__main__":
    with app.app_context():
        fetch_pokemon_data()
