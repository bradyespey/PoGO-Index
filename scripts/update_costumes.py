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
from models import Costume

# URL for event Pokémon costume data
URL = "https://pokemongo.fandom.com/wiki/Event_Pok%C3%A9mon#Regular"

def parse_event_pokemon(html):
    """Parse the HTML and extract event Pokémon costume data."""
    soup = BeautifulSoup(html, 'html.parser')
    event_items = soup.find_all("div", class_="pogo-list-item")
    parsed_data = []

    if not event_items:
        print("No event Pokémon items found.")
        return parsed_data

    for item in event_items:
        # Extract dex number
        dex_number_tag = item.find("div", class_="pogo-list-item-number")
        dex_number = int(dex_number_tag.get_text(strip=True).replace("#", "")) if dex_number_tag else None

        # Extract Pokémon name
        name_tag = item.find("div", class_="pogo-list-item-name")
        name = name_tag.get_text(strip=True) if name_tag else "Unknown"

        # Extract costume/form
        form_tag = item.find("div", class_="pogo-list-item-form")
        costume = form_tag.get_text(strip=True) if form_tag else "Unknown"

        # Check for shiny status and set shiny_released value
        shiny = item.find("div", class_="pogo-list-item-image shiny") is not None
        shiny_released = shiny

        # Extract image URLs with improved handling for nested tags
        image_url = None
        shiny_image_url = None

        # Find the regular image
        image_r_tag = item.find("div", class_="pogo-list-item-image-r")
        if image_r_tag:
            image = image_r_tag.find("img")
            if image and "src" in image.attrs:
                image_url = image["src"]

        # Find the shiny image
        image_s_tag = item.find("div", class_="pogo-list-item-image-s")
        if image_s_tag:
            shiny_image = image_s_tag.find("img")
            if shiny_image and "src" in shiny_image.attrs:
                shiny_image_url = shiny_image["src"]

        # Debug: Print image URLs to confirm parsing
        print(f"Parsed {name}: Dex #{dex_number}, Costume: {costume}, Image URL: {image_url}, Shiny Image URL: {shiny_image_url}")

        # Append data for processing
        parsed_data.append({
            "dex_number": dex_number,
            "name": name,
            "costume": costume,
            "image_url": image_url,
            "shiny_released": shiny_released,
            "shiny_image_url": shiny_image_url
        })

    return parsed_data

def fetch_costume_data():
    """Fetch and update costume Pokémon data in the database."""
    print("Fetching and updating Costume Pokémon data...")

    start_time = time.time()
    print(f"Fetching data from {URL}...")
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return

    soup = response.text
    costumes_data = parse_event_pokemon(soup)
    count_inserted, count_updated, count_skipped = 0, 0, 0

    for costume_data in costumes_data:
        # Check if costume entry exists
        existing_costume = Costume.query.filter_by(
            dex_number=costume_data["dex_number"],
            name=costume_data["name"],
            costume=costume_data["costume"]
        ).first()

        if existing_costume:
            # Update fields if needed
            if (existing_costume.image_url != costume_data["image_url"] or
                existing_costume.shiny_released != costume_data["shiny_released"] or
                existing_costume.shiny_image_url != costume_data["shiny_image_url"]):
                
                existing_costume.image_url = costume_data["image_url"]
                existing_costume.shiny_released = costume_data["shiny_released"]
                existing_costume.shiny_image_url = costume_data["shiny_image_url"]
                db.session.commit()
                count_updated += 1
            else:
                count_skipped += 1
        else:
            # Insert new costume entry
            print(f"Inserting new costume Pokémon {costume_data['name']} with dex number {costume_data['dex_number']}")
            new_costume = Costume(
                dex_number=costume_data["dex_number"],
                name=costume_data["name"],
                costume=costume_data["costume"],
                image_url=costume_data["image_url"],
                shiny_released=costume_data["shiny_released"],
                shiny_image_url=costume_data["shiny_image_url"],
                brady_own=False,
                brady_shiny=False,
                matt_own=False,
                matt_shiny=False
            )
            db.session.add(new_costume)
            db.session.commit()
            count_inserted += 1

    print(f"Finished processing Costume Pokémon")
    print(f"Total Costumes added: {count_inserted}")
    print(f"Total Costumes updated: {count_updated}")
    print(f"Total Costumes skipped: {count_skipped}")
    print(f"Fetched and processed data in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    with app.app_context():
        fetch_costume_data()