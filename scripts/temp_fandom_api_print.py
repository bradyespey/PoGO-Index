# scripts/temp_fandom_api_print.py

import fandom
import re
from pprint import pprint

# Set the Fandom wiki to Pokémon GO
fandom.set_wiki("pokemongo")

# Fetch the "Event Pokémon" page content
page = fandom.page("Event Pokémon")

# Verify that we retrieved the page
if page:
    print("Successfully retrieved page content.\n")
    
    # Extract the text content under 'content' key
    content_text = page.content.get("content", "")

    # Parse the content to find costume data
    def parse_costume_data(content):
        costume_data = []

        # Improved pattern to match entries like '#0001 Bulbasaur Halloween'
        # Splits costumes more reliably even if there's no whitespace
        pattern = re.compile(r"#(?P<dex_number>\d{3,4})\s*(?P<name>[A-Za-z]+?)(?=[A-Z][a-z])\s*(?P<costume>[A-Za-z\s]+)?")
        
        # Extract entries that match the pattern
        matches = pattern.findall(content)
        
        for match in matches:
            dex_number = int(match[0])
            name = match[1].strip()
            costume = match[2].strip() if match[2] else ""
            costume_data.append({
                "dex_number": dex_number,
                "name": name,
                "costume": costume
            })

        return costume_data

    # Extract costume Pokémon data from content_text
    costumes_data = parse_costume_data(content_text)

    # Output results
    print("Extracted Costume Pokémon Data:")
    pprint(costumes_data)

else:
    print("Failed to retrieve the page content.")
