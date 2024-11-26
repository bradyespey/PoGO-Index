# scripts/update_pokemon.py

import os
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup

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

        # Construct remote image URL
        image_filename = f"{name.lower().replace(' ', '-').replace(':', '')}.png"
        remote_image_url = f"https://img.pokemondb.net/sprites/scarlet-violet/icon/{image_filename}"

        # Fetch or create Pokémon entry in the database
        pokemon = Pokemon.query.filter_by(dex_number=dex_number).first()
        if not pokemon:
            print(f"Inserting new Pokémon {name} with dex number {dex_number}")
            pokemon = Pokemon(
                dex_number=dex_number,
                name=name,
                type=type_,
                image_url=remote_image_url,
                shiny_released=False,  # Default value, will be updated later
                notes='',  # Default value, can be updated later
                brady_living_dex=False,
                brady_shiny=False,  # Brady's Shiny
                brady_lucky=False,
                matt_living_dex=False,
                matt_shiny=False,  # Matt's Shiny (NEW)
                matt_lucky=False,
                ipad_living_dex=True,
                ipad_shiny=False,  # iPad's Shiny (NEW)
                ipad_lucky=False
            )
            db.session.add(pokemon)
            count_inserted += 1
        else:
            # Update image URL if it has changed
            if pokemon.image_url != remote_image_url:
                pokemon.image_url = remote_image_url
                count_updated += 1
            else:
                count_skipped += 1

            # Reset user-specific dex fields
            pokemon.brady_living_dex = False
            pokemon.brady_shiny = False  # Reset Brady's shiny column
            pokemon.brady_lucky = False
            pokemon.matt_shiny = False  # Reset Matt's shiny column (NEW)
            pokemon.ipad_shiny = False  # Reset iPad's shiny column (NEW)
            # Note: Keeping 'shiny_released' and 'notes' unchanged during update

        # Fetch PokeGenie entries for this Pokémon
        poke_genie_entries = PokeGenieEntry.query.filter_by(pokemon_number=dex_number).all()

        # Process each entry and update flags based on the specified logic
        for entry in poke_genie_entries:
            if not pokemon:
                print(f"Error: Pokémon with dex number {dex_number} not found.")
                continue

            # Brady's Living Dex logic
            if entry.lucky == 0 and entry.shadow_purified == 0 and (entry.favorite == 0 or entry.favorite == 4):
                pokemon.brady_living_dex = True

            # Brady's Shiny Dex logic
            if entry.lucky == 0 and entry.shadow_purified == 0 and entry.favorite == 1:
                pokemon.brady_shiny = True

            # Matt's Shiny Dex logic (NEW)
            if entry.lucky == 0 and entry.shadow_purified == 0 and entry.favorite == 2:
                pokemon.matt_shiny = True

            # Brady's Lucky Dex logic
            if entry.lucky == 1 and entry.shadow_purified == 0 and entry.favorite == 0:
                pokemon.brady_lucky = True

            # iPad's Shiny Dex logic (NEW)
            if entry.lucky == 0 and entry.shadow_purified == 0 and entry.favorite == 3:
                pokemon.ipad_shiny = True

            # iPad's Living Dex logic
            if entry.lucky == 0 and entry.shadow_purified == 0 and entry.favorite == 4:
                pokemon.ipad_living_dex = False

        # Commit changes for each Pokémon to the database
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to commit changes for Pokémon {name} (Dex {dex_number}): {e}")
            continue

    # Final output
    print(f"Finished processing {len(rows)} Pokémon")
    print(f"Total Pokémon added: {count_inserted}")
    print(f"Total Pokémon updated: {count_updated}")
    print(f"Total Pokémon skipped: {count_skipped}")
    print(f"Total Pokémon with image URL updates: {count_with_images}")

def update_shiny_released():
    print("Updating shiny_released status based on Serebii shiny list...")

    url = "https://www.serebii.net/pokemongo/shiny.shtml"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"Fetched shiny data from {url} successfully.")
    except requests.RequestException as e:
        print(f"Error fetching shiny data from {url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all("table")

    if len(tables) < 2:
        print("Expected at least 2 tables on the shiny page.")
        return

    shiny_table = tables[1]  # Assuming the second table contains shiny data
    rows = shiny_table.find_all("tr")[1:]  # Skip the header row
    print(f"Found {len(rows)} Shiny Pokémon entries.")

    shiny_dex_numbers = set()

    for row in rows:
        cols = row.find_all("td", recursive=False)

        if len(cols) < 5:
            continue

        dex_number_text = cols[0].get_text(strip=True).replace('#', '')
        if not dex_number_text.isdigit():
            print(f"Invalid dex number '{dex_number_text}' found. Skipping row.")
            continue
        dex_number = int(dex_number_text)
        shiny_dex_numbers.add(dex_number)

    # Reset all shiny_released to False
    try:
        Pokemon.query.update({Pokemon.shiny_released: False})
        db.session.commit()
        print("Reset shiny_released for all Pokémon to False.")
    except Exception as e:
        db.session.rollback()
        print(f"Error resetting shiny_released: {e}")
        return

    # Set shiny_released to True for Pokémon in the shiny_dex_numbers set
    try:
        updated_count = Pokemon.query.filter(Pokemon.dex_number.in_(shiny_dex_numbers)).update(
            {Pokemon.shiny_released: True},
            synchronize_session=False
        )
        db.session.commit()
        print(f"Set shiny_released to True for {updated_count} Pokémon.")
    except Exception as e:
        db.session.rollback()
        print(f"Error updating shiny_released: {e}")

if __name__ == "__main__":
    with app.app_context():
        fetch_pokemon_data()
        update_shiny_released()