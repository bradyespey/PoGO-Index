from app import app, db
from models import Pokemon

with app.app_context():
    # Query the Pokémon with ID 9999 to confirm it exists
    inserted_pokemon = Pokemon.query.filter_by(id=9999).first()

    if inserted_pokemon:
        print(f"Pokémon with ID 9999 exists: {inserted_pokemon.name}, {inserted_pokemon.type}")
    else:
        print("No Pokémon with ID 9999 found.")