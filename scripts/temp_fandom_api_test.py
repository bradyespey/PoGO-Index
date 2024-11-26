# scripts/temp_fandom_api_test.py

import requests
from bs4 import BeautifulSoup

def fetch_first_10_shiny_images():
    """Fetch and print the first 10 shiny Pokémon images from the Event Pokémon page."""
    url = "https://pokemongo.fandom.com/wiki/Event_Pok%C3%A9mon"
    
    print(f"Fetching data from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
    except requests.RequestException as e:
        print(f"An error occurred while fetching the page: {e}")
        return

    # Parse the HTML content to locate the shiny images
    soup = BeautifulSoup(html_content, 'html.parser')
    shiny_items = soup.select("div.pogo-list-item-image.shiny div.pogo-list-item-image-s img")

    shiny_images = []
    count = 0

    for img_tag in shiny_items:
        if count >= 10:
            break

        # Extract the shiny image URL
        shiny_image_url = img_tag.get("data-src") or img_tag.get("src")
        if shiny_image_url:
            # Clean up the URL
            shiny_image_url = shiny_image_url.split('?')[0].split('/revision/')[0]
            shiny_images.append(shiny_image_url)
            print(f"Shiny Image URL: {shiny_image_url}")
            count += 1

    if not shiny_images:
        print("No shiny images found.")
    else:
        print(f"\nFirst {len(shiny_images)} shiny images fetched successfully.")

if __name__ == "__main__":
    fetch_first_10_shiny_images()