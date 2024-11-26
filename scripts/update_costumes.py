# scripts/update_cosutmes.py

import os
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Importing the app and db for database management
from app import app, db
from models import Costume

def fetch_costume_data():
    """Fetch and update costume Pokémon data in the database without resetting the table."""
    print("Fetching and updating Costume Pokémon data...")

    start_time = time.time()
    url = "https://pokemongo.fandom.com/wiki/Event_Pok%C3%A9mon"

    print(f"Fetching data from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
    except requests.RequestException as e:
        print(f"An error occurred while fetching the page: {e}")
        return

    # Parse the HTML content to extract the event Pokémon data
    costumes_data = parse_event_pokemon(html_content)

    # Now update the database
    update_database(costumes_data)

    print(f"\nFinished processing {len(costumes_data)} Costume Pokémon")
    print(f"Fetched and processed data in {time.time() - start_time:.2f} seconds")

def parse_event_pokemon(html):
    """Parse the HTML and extract event Pokémon costume data, including images."""
    soup = BeautifulSoup(html, 'html.parser')
    parsed_data = {}
    
    # Find all tabs (Regular, Shiny, and Extra Forms)
    tabs = soup.find_all("div", class_="wds-tab__content")
    
    # Iterate over all tabs
    for idx, tab in enumerate(tabs):
        # Determine if this tab is for shiny Pokémon based on index or some other attribute
        # For simplicity, let's assume:
        # idx == 0: Regular
        # idx == 1: Shiny
        # idx >= 2: Extra Forms (Shiny)
        shiny = idx != 0  # All tabs except the first are for shiny Pokémon

        # Find all costume Pokémon in this tab
        items = tab.find_all("div", class_="pogo-list-item")

        for item in items:
            # Extract dex number
            dex_number_tag = item.find("div", class_="pogo-list-item-number")
            dex_number_text = dex_number_tag.get_text(strip=True).replace("#", "") if dex_number_tag else None
            try:
                dex_number = int(dex_number_text)
            except (ValueError, TypeError):
                dex_number = None

            # Extract Pokémon name
            name_tag = item.find("div", class_="pogo-list-item-name")
            name_link = name_tag.find("a") if name_tag else None
            name = name_link.get_text(strip=True) if name_link else name_tag.get_text(strip=True) if name_tag else "Unknown"

            # Extract costume/form
            form_tag = item.find("div", class_="pogo-list-item-form")
            costume = form_tag.get_text(strip=True) if form_tag else None

            # Extract images
            image_url = None
            shiny_image_url = None

            # Extract image divs
            image_div_r = item.find("div", class_="pogo-list-item-image-r")
            image_div_s = item.find("div", class_="pogo-list-item-image-s")

            # For regular entries
            if not shiny:
                if image_div_r:
                    img_tag = image_div_r.find("img")
                    if img_tag:
                        image_url = img_tag.get("data-src") or img_tag.get("src")
                        if image_url:
                            image_url = image_url.split('?')[0].split('/revision/')[0]
            else:
                # For shiny entries
                if image_div_r:
                    img_tag = image_div_r.find("img")
                    if img_tag:
                        shiny_image_url = img_tag.get("data-src") or img_tag.get("src")
                        if shiny_image_url:
                            shiny_image_url = shiny_image_url.split('?')[0].split('/revision/')[0]
                elif image_div_s:
                    img_tag = image_div_s.find("img")
                    if img_tag:
                        shiny_image_url = img_tag.get("data-src") or img_tag.get("src")
                        if shiny_image_url:
                            shiny_image_url = shiny_image_url.split('?')[0].split('/revision/')[0]

            if dex_number is None or name == "Unknown":
                continue

            key = (dex_number, name, costume)

            if key not in parsed_data:
                parsed_data[key] = {
                    "dex_number": dex_number,
                    "name": name,
                    "costume": costume,
                    "image_url": None,
                    "shiny_image_url": None,
                }

            # Update the appropriate image URLs
            if not shiny:
                if image_url:
                    parsed_data[key]["image_url"] = image_url
            else:
                if shiny_image_url:
                    parsed_data[key]["shiny_image_url"] = shiny_image_url

    return list(parsed_data.values())

def update_database(costumes_data):
    """Update the database with the parsed costume data."""
    count_inserted, count_updated, count_skipped = 0, 0, 0

    with app.app_context():
        for costume_data in costumes_data:
            dex_number = costume_data["dex_number"]
            name = costume_data["name"]
            costume = costume_data["costume"]

            # Skip if dex_number or name is None
            if dex_number is None or name == "Unknown":
                continue

            # Check if the costume already exists in the table
            existing_costume = Costume.query.filter_by(
                dex_number=dex_number,
                name=name,
                costume=costume
            ).first()

            if existing_costume:
                # Update fields if any of them has changed
                updated_fields = []
                if existing_costume.image_url != costume_data.get("image_url"):
                    existing_costume.image_url = costume_data.get("image_url")
                    updated_fields.append("image_url")
                if existing_costume.shiny_image_url != costume_data.get("shiny_image_url"):
                    existing_costume.shiny_image_url = costume_data.get("shiny_image_url")
                    updated_fields.append("shiny_image_url")

                # Commit changes if any fields were updated
                if updated_fields:
                    db.session.commit()
                    count_updated += 1
                    print(f"Updated {name} (Dex #{dex_number}, Costume: {costume}) fields: {', '.join(updated_fields)}")
                else:
                    count_skipped += 1
            else:
                # Insert new costume entry
                print(f"Inserting new costume Pokémon {name} (Dex #{dex_number}), Costume: {costume}")
                new_costume = Costume(
                    dex_number=dex_number,
                    name=name,
                    costume=costume,
                    image_url=costume_data.get("image_url"),
                    shiny_image_url=costume_data.get("shiny_image_url"),
                    brady_own=False,
                    brady_shiny=False,
                    matt_own=False,
                    matt_shiny=False
                )
                db.session.add(new_costume)
                count_inserted += 1

        db.session.commit()

    print(f"Total Costumes added: {count_inserted}")
    print(f"Total Costumes updated: {count_updated}")
    print(f"Total Costumes skipped (no changes needed): {count_skipped}")

if __name__ == "__main__":
    # Fetch and populate costume data without resetting the table
    with app.app_context():
        fetch_costume_data()