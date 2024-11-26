# routes.py

from flask import (
    render_template, redirect, url_for, jsonify, request, session
)
from functools import wraps
from models import (
    db, Pokemon, Note, PokeGenieEntry,
    ShinyPokemon, Rocket, Costume, Form, User, AllPokemon
)

# Authentication decorator
def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))  # Redirect to login with 'next' URL
        return f(*args, **kwargs)
    return decorated_function

def init_routes(app, google):

    # Helper function to check authentication
    def is_user_authenticated():
        return 'user' in session

    ### Public Routes ###

    # Info page route
    @app.route('/')
    @app.route('/pogo')
    @app.route('/pogo/info')
    def info_page():
        # Counts from PokeGenieEntry
        shiny_count = PokeGenieEntry.query.filter_by(favorite=1).count()
        costume_count = PokeGenieEntry.query.filter_by(favorite=2).count()
        shiny_costume_count = PokeGenieEntry.query.filter_by(favorite=3).count()
        ipad_need_count = PokeGenieEntry.query.filter_by(favorite=4).count()
        extras_count = PokeGenieEntry.query.filter_by(favorite=5).count()

        lucky_count = PokeGenieEntry.query.filter_by(lucky=1).count()
        shadow_count = PokeGenieEntry.query.filter_by(shadow_purified=1).count()
        purified_count = PokeGenieEntry.query.filter_by(shadow_purified=2).count()

        # Calculate remaining Brady living dex count
        total_pokemon_count = Pokemon.query.count()

        # Query PokeGenieEntry for entries that satisfy brady_living_dex 'Yes' conditions
        poke_genie_entries = PokeGenieEntry.query.filter_by(
            lucky=0, shadow_purified=0
        ).filter(PokeGenieEntry.favorite.in_([0, 4])).all()

        brady_living_dex_ids = {entry.pokemon_number for entry in poke_genie_entries}

        # Remaining living dex count
        remaining_living_dex_count = total_pokemon_count - len(brady_living_dex_ids)

        return render_template(
            'info.html',
            shiny_count=shiny_count,
            costume_count=costume_count,
            shiny_costume_count=shiny_costume_count,
            ipad_need_count=ipad_need_count,
            extras_count=extras_count,
            lucky_count=lucky_count,
            shadow_count=shadow_count,
            purified_count=purified_count,
            remaining_living_dex_count=remaining_living_dex_count
        )

    # Pokémon page route
    @app.route('/pogo/pokemon')
    def pokemon():
        # Fetch all Pokémon entries
        pokemon_list = Pokemon.query.all()
        extended_pokemon_list = []

        # Fetch Matt's user based on email
        matt = User.query.filter_by(email='matt@example.com').first()  # Replace with Matt's actual email

        # Get the set of Pokémon IDs that Matt owns
        matt_owned_ids = set()
        if matt:
            matt_owned_ids = {op.pokemon_id for op in matt.owned_pokemon}

        # Create mappings from dex_number to category and generation from AllPokemon table
        all_pokemon_entries = AllPokemon.query.all()
        dex_to_category = {entry.dex_number: entry.category for entry in all_pokemon_entries}
        dex_to_generation = {entry.dex_number: entry.generation for entry in all_pokemon_entries}

        # Fetch distinct categories and generations for filter dropdowns
        categories = sorted({entry.category for entry in all_pokemon_entries if entry.category})
        generations = sorted({entry.generation for entry in all_pokemon_entries if entry.generation})
        
        # Fetch distinct types for filter dropdown
        types = sorted({pokemon.type for pokemon in pokemon_list if pokemon.type})

        for pokemon in pokemon_list:
            # Updated user-specific dex fields
            brady_living_dex = 'Yes' if pokemon.brady_living_dex else 'No'
            brady_shiny_dex = 'Yes' if pokemon.brady_shiny else 'No'
            brady_lucky_dex = 'Yes' if pokemon.brady_lucky else 'No'
            need_on_ipad = 'Yes' if pokemon.ipad_living_dex else 'No'
            ipad_lucky_dex = 'Yes' if pokemon.ipad_lucky else 'No'
            ipad_shiny_dex = 'Yes' if pokemon.ipad_shiny else 'No'

            matt_have = 'Yes' if pokemon.matt_living_dex else 'No'
            matt_lucky = 'Yes' if pokemon.matt_lucky else 'No'
            matt_shiny = 'Yes' if pokemon.matt_shiny else 'No'

            # Fetch category and generation from AllPokemon
            category = dex_to_category.get(pokemon.dex_number, 'Unknown')
            generation = dex_to_generation.get(pokemon.dex_number, 'Unknown')

            # Note Text
            note_text = pokemon.notes if pokemon.notes else ''

            # Append extended data
            extended_pokemon_list.append({
                'id': pokemon.id,
                'dex_number': pokemon.dex_number,
                'name': pokemon.name,
                'type': pokemon.type,
                'image_url': pokemon.image_url,
                'shiny_released': 'Yes' if pokemon.shiny_released else 'No',
                'notes': note_text,
                'brady_living_dex': brady_living_dex,
                'brady_shiny_dex': brady_shiny_dex,
                'brady_lucky_dex': brady_lucky_dex,
                'matt_have': matt_have,
                'matt_lucky': matt_lucky,
                'matt_shiny': matt_shiny,
                'need_on_ipad': need_on_ipad,
                'ipad_lucky_dex': ipad_lucky_dex,
                'ipad_shiny_dex': ipad_shiny_dex,
                'category': category,
                'generation': generation,
            })

        return render_template(
            'pokemon.html',
            pokemon_list=extended_pokemon_list,
            categories=categories,
            generations=generations,
            types=types
        )
    
    @app.route('/pogo/save-all-changes', methods=['POST'])
    @requires_auth
    def save_all_changes():
        data = request.get_json()

        # Debugging: Log the entire received JSON data
        print("Received JSON data:", data)

        # Ensure data is received correctly
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # === Process Notes Data ===
        notes = data.get('notes', [])
        for note in notes:
            pokemon_id = note.get('pokemon_id')
            note_text = note.get('note')
            if pokemon_id:
                pokemon = Pokemon.query.filter_by(id=pokemon_id).first()
                if pokemon:
                    pokemon.notes = note_text  # Update the notes directly in the Pokemon table

        # === Process Checkbox Data ===
        for checkbox in data.get('checkboxes', []):
            entity_id = checkbox.get('shiny_id') or checkbox.get('pokemon_id') or checkbox.get('costume_id') or checkbox.get('rocket_id')
            checkbox_type = checkbox.get('type')
            checked_value = checkbox.get('value') == 'Yes'

            # Debugging: Log the entity being processed
            print(f"Processing checkbox: entity_id={entity_id}, type={checkbox_type}, value={checked_value}")

            # Process checkboxes for Shiny Pokémon
            if checkbox_type.startswith('shiny_'):
                shiny_pokemon = ShinyPokemon.query.filter_by(id=entity_id).first()
                if shiny_pokemon:
                    if checkbox_type == 'shiny_brady_own':
                        shiny_pokemon.brady_own = checked_value
                    elif checkbox_type == 'shiny_brady_lucky':
                        shiny_pokemon.brady_lucky = checked_value
                    elif checkbox_type == 'shiny_matt_own':
                        shiny_pokemon.matt_own = checked_value
                    elif checkbox_type == 'shiny_matt_lucky':
                        shiny_pokemon.matt_lucky = checked_value
                    db.session.add(shiny_pokemon)

            # Process checkboxes for normal Pokémon
            elif checkbox_type in ['matt_lucky', 'matt_have', 'ipad_lucky', 'matt_shiny', 'ipad_shiny']:
                pokemon = Pokemon.query.filter_by(id=entity_id).first()
                if pokemon:
                    if checkbox_type == 'matt_lucky':
                        pokemon.matt_lucky = checked_value
                    elif checkbox_type == 'matt_have':
                        pokemon.matt_living_dex = checked_value
                    elif checkbox_type == 'ipad_lucky':
                        pokemon.ipad_lucky = checked_value
                    elif checkbox_type == 'matt_shiny':
                        pokemon.matt_shiny = checked_value
                    elif checkbox_type == 'ipad_shiny':
                        pokemon.ipad_shiny = checked_value
                    db.session.add(pokemon)

            # Process checkboxes for Costumes
            elif checkbox_type.startswith('costume_'):
                costume = Costume.query.filter_by(id=entity_id).first()
                if costume:
                    if checkbox_type == 'costume_brady_own':
                        costume.brady_own = checked_value
                    elif checkbox_type == 'costume_brady_shiny':
                        costume.brady_shiny = checked_value
                    elif checkbox_type == 'costume_matt_own':
                        costume.matt_own = checked_value
                    elif checkbox_type == 'costume_matt_shiny':
                        costume.matt_shiny = checked_value
                    db.session.add(costume)

            # Process checkboxes for Rocket Pokémon
            elif checkbox_type.startswith('rocket_'):
                rocket_pokemon = Rocket.query.filter_by(id=entity_id).first()
                if rocket_pokemon:
                    if checkbox_type == 'rocket_matt_shadow':
                        rocket_pokemon.matt_shadow = checked_value
                    elif checkbox_type == 'rocket_matt_purified':
                        rocket_pokemon.matt_purified = checked_value
                    db.session.add(rocket_pokemon)
                    # Debugging: Confirm update for Rocket Pokémon
                    print(f"Updated Rocket Pokémon: id={rocket_pokemon.id}, matt_shadow={rocket_pokemon.matt_shadow}, matt_purified={rocket_pokemon.matt_purified}")

        # === Commit All Changes to the Database ===
        try:
            db.session.commit()
            print("Changes committed successfully.")
            return jsonify({'message': 'Changes saved successfully'}), 200
        except Exception as e:
            db.session.rollback()
            print("Database commit failed:", e)
            return jsonify({'error': str(e)}), 500

    # Poke Genie page route
    @app.route('/pogo/poke-genie')
    def poke_genie():
        poke_genie_data = PokeGenieEntry.query.all()
        return render_template('poke_genie.html', poke_genie_data=poke_genie_data)

    # Shinies page route
    @app.route('/pogo/shinies')
    def shinies():
        shinies_data = ShinyPokemon.query.all()
        extended_shinies_list = []

        for shiny in shinies_data:
            # Create a dictionary with all the details for each shiny Pokémon
            extended_shinies_list.append({
                'id': shiny.id,
                'dex_number': shiny.dex_number,
                'name': shiny.name,
                'form': shiny.form if shiny.form else 'Normal',  # Default to 'Normal' if no form specified
                'method': shiny.method,
                'brady_own': 'Yes' if shiny.brady_own else 'No',
                'brady_lucky': 'Yes' if shiny.brady_lucky else 'No',
                'matt_own': 'Yes' if shiny.matt_own else 'No',
                'matt_lucky': 'Yes' if shiny.matt_lucky else 'No'
            })

        return render_template('shinies.html', shinies_list=extended_shinies_list)

    # Costumes page route
    @app.route('/pogo/costumes')
    def costumes():
        costumes_data = Costume.query.all()
        extended_costumes_list = []

        for costume in costumes_data:
            # Create a dictionary with all the details for each costume Pokémon
            extended_costumes_list.append({
                'id': costume.id,
                'dex_number': costume.dex_number,
                'name': costume.name,
                'costume': costume.costume,
                'image_url': costume.image_url,
                'shiny_image_url': costume.shiny_image_url,
                'brady_own': 'Yes' if costume.brady_own else 'No',
                'matt_own': 'Yes' if costume.matt_own else 'No',
                'brady_shiny': 'Yes' if costume.brady_shiny else 'No',
                'matt_shiny': 'Yes' if costume.matt_shiny else 'No'
            })

        return render_template('costumes.html', costumes_data=extended_costumes_list)

    # Forms page route
    @app.route('/pogo/forms')
    def forms():
        forms_data = Form.query.all()
        return render_template('forms.html', forms_data=forms_data)

    # Rocket page route
    @app.route('/pogo/rocket')
    def rocket():
        rocket_data = Rocket.query.all()  # Fetch all entries from Rocket table
        updated_rocket_data = []

        for rocket_pokemon in rocket_data:
            try:
                dex_number = int(rocket_pokemon.dex_number)  # Ensure this is an integer
            except ValueError:
                print(f"Invalid dex_number format: {rocket_pokemon.dex_number}")
                continue  # Skip if the dex_number isn't valid

            # Initialize default values for Brady's shadow and purified columns
            brady_shadow = 'No'
            brady_purified = 'No'

            # Query for Brady's shadow dex (lucky = 0, favorite = 0, shadow_purified = 1)
            brady_shadow_entries = PokeGenieEntry.query.filter_by(
                pokemon_number=dex_number, lucky=0, favorite=0, shadow_purified=1
            ).all()
            if brady_shadow_entries:
                brady_shadow = 'Yes'  # Mark as 'Yes' if any entry matches the condition

            # Query for Brady's purified dex (lucky = 0, favorite = 0, shadow_purified = 2)
            brady_purified_entries = PokeGenieEntry.query.filter_by(
                pokemon_number=dex_number, lucky=0, favorite=0, shadow_purified=2
            ).all()
            if brady_purified_entries:
                brady_purified = 'Yes'  # Mark as 'Yes' if any entry matches the condition

            # Append rocket data with all fields, including 'id'
            print(f"Rocket Pokémon ID: {rocket_pokemon.id} Name: {rocket_pokemon.name}")
            updated_rocket_data.append({
                'id': rocket_pokemon.id,
                'dex_number': rocket_pokemon.dex_number,
                'name': rocket_pokemon.name,
                'method': rocket_pokemon.method,
                'brady_shadow': brady_shadow,
                'brady_purified': brady_purified,
                'matt_shadow': 'Yes' if rocket_pokemon.matt_shadow else 'No',
                'matt_purified': 'Yes' if rocket_pokemon.matt_purified else 'No'
            })

        print("Updated Rocket Data: ", updated_rocket_data)
        return render_template('rocket.html', rocket_data=updated_rocket_data)
    
    # All Pokémon page route
    @app.route('/pogo/all-pokemon')
    def all_pokemon():
        all_pokemon_data = AllPokemon.query.all()
        return render_template('all_pokemon.html', all_pokemon_data=all_pokemon_data)

    # Notes page route
    @app.route('/pogo/notes')
    def notes():
        notes_data = db.session.query(Note, Pokemon.name).join(
            Pokemon, Note.pokemon_id == Pokemon.id
        ).all()
        return render_template('notes.html', notes_data=notes_data)

    # API route for Pokemon
    @app.route('/pogo/api/pokemon')
    def get_pokemon():
        pokemon_list = Pokemon.query.all()
        return jsonify([{
            "name": p.name,
            "type": p.type.split(','),
            "image_url": p.image_url
        } for p in pokemon_list])

    # Authentication Routes ###

    # Check if the user is authenticated
    @app.route('/pogo/is_authenticated')
    def check_authenticated():
        return jsonify({'authenticated': 'user' in session})

    # Login route
    @app.route('/pogo/login')
    def login():
        # Capture the current page URL to return to after login
        next_url = request.args.get('next') or request.referrer or url_for('info_page')
        session['next_url'] = next_url  # Store the URL in the session

        # Redirect to Google OAuth
        redirect_url = url_for('authorize', _external=True)
        print(f"Google OAuth redirect URL: {redirect_url}")  # Log the redirect URI being used
        return google.authorize_redirect(redirect_url)

    # OAuth2 callback route after user authenticates
    @app.route('/pogo/oauth2callback')
    def authorize():
        token = google.authorize_access_token()
        if token is None:
            return "Authorization failed.", 400
        session['user'] = token  # Save user token in session

        # Get the next URL from the session (default to 'info_page' if not available)
        next_url = session.pop('next_url', url_for('info_page'))
        return redirect(next_url)

    # Logout route to clear the session
    @app.route('/pogo/logout')
    def logout():
        # Capture the current page URL to return to after logout
        next_url = request.args.get('next') or request.referrer or url_for('info_page')

        # Clear all session data related to the user
        session.clear()
        return redirect(next_url)  # Redirect to the captured URL

    ### Protected Routes ###

    # Route to trigger Pokemon data update
    @app.route('/pogo/update-now', methods=['POST'])
    @requires_auth
    def update_now():
        from scripts.update_pokemon import fetch_pokemon_data  # Move import here
        with app.app_context():
            fetch_pokemon_data()
        return redirect(url_for('pokemon'))

    # Update Poke Genie data route
    @app.route('/pogo/update-poke-genie', methods=['POST'])
    @requires_auth
    def update_poke_genie():
        from scripts.update_poke_genie import import_poke_genie_data  # Move import here
        with app.app_context():
            import_poke_genie_data()
        return redirect(url_for('poke_genie'))

   # Update Shinies data route
    @app.route('/pogo/update-shinies', methods=['POST'])
    @requires_auth
    def update_shinies():
        from scripts.update_shinies import fetch_shiny_pokemon_data  # Move import here
        with app.app_context():
            fetch_shiny_pokemon_data()
        return redirect(url_for('shinies'))
    
    # Update Costumes data route
    @app.route('/pogo/update-costumes', methods=['POST'])
    @requires_auth
    def update_costumes():
        from scripts.update_costumes import fetch_costume_pokemon_data  # Import function here
        with app.app_context():
            fetch_costume_pokemon_data()
        return redirect(url_for('costumes'))

   # Update Rocket data route
    @app.route('/pogo/update-rocket', methods=['POST'])
    @requires_auth
    def update_rocket():
        from scripts.update_rocket import fetch_rocket_pokemon_data  # Move import here
        with app.app_context():
            fetch_rocket_pokemon_data()
        return redirect(url_for('rocket'))
    
    # Update All Pokémon data route
    @app.route('/pogo/update-all-pokemon', methods=['POST'])
    @requires_auth  # Ensure only authorized users can update
    def update_all_pokemon():
        from scripts.update_all_pokemon import fetch_all_pokemon_data
        with app.app_context():
            fetch_all_pokemon_data()
        return redirect(url_for('all_pokemon'))

    # Update Notes route
    @app.route('/pogo/update-notes', methods=['POST'])
    @requires_auth
    def update_notes():
        try:
            data = request.get_json()
            notes = data.get('notes', [])
            if not notes:
                return jsonify({'error': 'No notes received'}), 400

            for note in notes:
                pokemon_id = note.get('pokemon_id')
                note_text = note.get('note')
                if not pokemon_id:
                    continue
                existing_note = Note.query.filter_by(pokemon_id=pokemon_id).first()
                if existing_note:
                    existing_note.note_text = note_text
                else:
                    new_note = Note(pokemon_id=pokemon_id, note_text=note_text)
                    db.session.add(new_note)

            db.session.commit()
            return jsonify({'message': 'Notes updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500