# scripts/update_forms.py

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
from models import Form

def fetch_forms_data(app_context):
    with app_context:
        print("Fetching and updating Pokémon Forms data...")

        url = "https://pokemongo.fandom.com/wiki/List_of_Pok%C3%A9mon_with_different_forms"
        start_time = time.time()
        print(f"Fetching data from {url}...")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Fetched data in {time.time() - start_time:.2f} seconds")

        # Parse the forms data based on the HTML structure
        forms_data = []
        tables = soup.find_all('table')

        # Iterate through tables and extract relevant data (modify logic if structure changes)
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip the header row
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 3:  # Ensure there are enough columns
                    dex_number = int(columns[0].get_text(strip=True).replace('#', ''))  # Dex number
                    name = columns[1].get_text(strip=True)  # Pokémon name
                    form = columns[2].get_text(strip=True)  # Pokémon form
                    forms_data.append((dex_number, name, form))

        count_inserted, count_updated, count_skipped = 0, 0, 0

        for dex_number, name, form in forms_data:
            existing_form = Form.query.filter_by(dex_number=dex_number, name=name).first()

            if existing_form:
                # Update the record if the form has changed
                if existing_form.form != form:
                    existing_form.form = form
                    db.session.commit()
                    count_updated += 1
                else:
                    count_skipped += 1
            else:
                # Insert new entry
                print(f"Inserting new form Pokémon {name} with dex number {dex_number} and form {form}")
                new_form = Form(dex_number=dex_number, name=name, form=form)
                db.session.add(new_form)
                db.session.commit()
                count_inserted += 1

        # Final output summary
        print(f"Finished processing {len(forms_data)} forms")
        print(f"Total Forms added: {count_inserted}")
        print(f"Total Forms updated: {count_updated}")
        print(f"Total Forms skipped: {count_skipped}")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        fetch_forms_data(app.app_context())
