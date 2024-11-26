# scripts/temp_fandom_api_db.py

import os
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
from sqlalchemy import inspect, Table, MetaData, select, text
from sqlalchemy.exc import IntegrityError

# Clear the terminal
os.system('clear')

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Importing the app and db for database management
from app import app, db
from models import Costume

def reset_table(table_name):
    """Delete all entries in a specific table."""
    with app.app_context():
        print(f"Clearing all entries in table '{table_name}'...")
        db.session.execute(text(f'DELETE FROM {table_name}'))
        db.session.commit()
        print(f"All entries in '{table_name}' have been cleared.")

def parse_event_pokemon(html, shiny=False):
    """Parse the HTML and extract event Pokémon costume data, handling regular and shiny images separately."""
    soup = BeautifulSoup(html, 'html.parser')

    parsed_data = []

    if shiny:
        # Directly find all shiny image elements
        shiny_items = soup.select("div.pogo-list-item-image.shiny div.pogo-list-item-image-s img")

        for img_tag in shiny_items:
            # Extract dex number, name, and costume information from the surrounding elements
            item = img_tag.find_parent("div", class_="pogo-list-item")
            if not item:
                continue

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
            costume = form_tag.get_text(strip=True) if form_tag else "Unknown"

            # Extract the shiny image URL
            shiny_image_url = img_tag.get("data-src") or img_tag.get("src")
            if shiny_image_url:
                # Clean up the URL
                shiny_image_url = shiny_image_url.split('?')[0].split('/revision/')[0]
                parsed_data.append({
                    "dex_number": dex_number,
                    "name": name,
                    "costume": costume,
                    "shiny_image_url": shiny_image_url
                })
                print(f"Shiny Image URL for {name} (Dex #{dex_number}, Costume: {costume}): {shiny_image_url}")
    else:
        # Regular images processing
        event_tab = soup.find("div", class_="wds-tab__content wds-is-current")
        event_items = event_tab.find_all("div", class_="pogo-list-item") if event_tab else []

        for item in event_items:
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
            costume = form_tag.get_text(strip=True) if form_tag else "Unknown"

            # Find the regular image within 'pogo-list-item-image-s'
            image_s_tag = item.find("div", class_="pogo-list-item-image-s")
            if image_s_tag:
                regular_image = image_s_tag.find("img")
                if regular_image:
                    image_url = regular_image.get("data-src") or regular_image.get("src")
                    if image_url:
                        image_url = image_url.split('?')[0].split('/revision/')[0]
                    parsed_data.append({
                        "dex_number": dex_number,
                        "name": name,
                        "costume": costume,
                        "image_url": image_url
                    })
                    print(f"Regular Image URL for {name} (Dex #{dex_number}, Costume: {costume}): {image_url}")

    return parsed_data

def fetch_costume_data():
    """Fetch and update costume Pokémon data in the database."""
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
    regular_costumes_data = parse_event_pokemon(html_content, shiny=False)
    shiny_costumes_data = parse_event_pokemon(html_content, shiny=True)

    # Combine the data based on dex_number, name, and costume
    costumes_data = {}
    for data in regular_costumes_data + shiny_costumes_data:
        key = (data["dex_number"], data["name"], data["costume"])
        if key not in costumes_data:
            costumes_data[key] = data
        else:
            # Update shiny image URL if it's already stored as a regular entry
            costumes_data[key].update(data)

    count_inserted = 0

    with app.app_context():
        for costume_data in costumes_data.values():
            dex_number = costume_data["dex_number"]
            name = costume_data["name"]
            costume = costume_data["costume"]

            # Skip if dex_number or name is None
            if dex_number is None or name == "Unknown":
                continue

            # Check if the costume already exists in the table to prevent duplicates
            existing_costume = Costume.query.filter_by(
                dex_number=dex_number,
                name=name,
                costume=costume
            ).first()

            if existing_costume:
                print(f"Skipping duplicate entry for {name} (Dex #{dex_number}), Costume: {costume}")
                continue

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

    print(f"\nFinished processing {len(costumes_data)} Costume Pokémon")
    print(f"Total Costumes added: {count_inserted}")
    print(f"Fetched and processed data in {time.time() - start_time:.2f} seconds")

def output_table_entries():
    """Output the first 10 rows of the 'costumes' table."""
    with app.app_context():
        # Get the inspector for the database
        inspector = inspect(db.engine)
        all_tables = inspector.get_table_names()
        if 'costumes' not in all_tables:
            print("Table 'costumes' not found in the database.")
            return

        print(f"\nFirst 10 rows for 'costumes' table:")

        # Reflect the table
        metadata = MetaData()
        table = Table('costumes', metadata, autoload_with=db.engine)

        # Get column names
        columns = [str(column.name) for column in table.columns]
        print(", ".join(columns))

        # Build a select query for the first 10 rows
        stmt = select(table).limit(10)

        # Execute the query and print results
        result = db.session.execute(stmt)
        rows = result.fetchall()
        if not rows:
            print("No entries found.")
            return

        for row in rows:
            row_mapping = row._mapping
            row_data = [str(row_mapping.get(col, '')) for col in columns]
            print(", ".join(row_data))

if __name__ == "__main__":
    # Step 1: Reset the costumes table
    reset_table("costumes")
    
    # Step 2: Fetch and populate costume data with regular and shiny images
    fetch_costume_data()
    
    # Step 3: Output the first 10 rows for verification
    output_table_entries()