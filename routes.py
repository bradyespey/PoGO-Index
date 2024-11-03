from flask import (
    render_template, redirect, url_for, jsonify, request, session
)
from functools import wraps
from models import (
    db, Pokemon, Note, SpecialsPokemon, PokeGenieEntry,
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
        pokemon_list = Pokemon.query.all()
        extended_pokemon_list = []

        # Fetch Matt's user (based on user_2_living_dex now)
        matt = User.query.filter_by(email='matt@example.com').first()  # Replace with Matt's actual email

        # Get the set of Pokémon IDs that Matt owns
        matt_owned_ids = set()
        if matt:
            matt_owned_ids = {op.pokemon_id for op in matt.owned_pokemon}

        # Create a mapping from dex_number to category from AllPokemon table
        all_pokemon_entries = AllPokemon.query.all()
        dex_to_category = {entry.dex_number: entry.category for entry in all_pokemon_entries}

        for pokemon in pokemon_list:
            # Use the existing user-specific dex fields from the updated model
            brady_living_dex = 'Yes' if pokemon.user_1_living_dex else 'No'
            brady_lucky_dex = 'Yes' if pokemon.user_1_lucky else 'No'
            need_on_ipad = 'Yes' if pokemon.user_0_living_dex else 'No'
            ipad_lucky_dex = 'Yes' if pokemon.user_0_lucky else 'No'

            # Matt's Have Living Dex Logic (user_2_living_dex is used now)
            matt_have = 'Yes' if pokemon.user_2_living_dex else 'No'
            matt_lucky = 'Yes' if pokemon.user_2_lucky else 'No'

            # Fetch category from AllPokemon
            category = dex_to_category.get(pokemon.dex_number)
            legendary, mythical, ultra_beast = 'No', 'No', 'No'
            if category:
                categories_list = [cat.strip() for cat in category.split(',')]
                if 'Legendary' in categories_list:
                    legendary = 'Yes'
                if 'Mythical' in categories_list:
                    mythical = 'Yes'
                if 'Ultra Beast' in categories_list:
                    ultra_beast = 'Yes'

            # Note Text
            note_entry = Note.query.filter_by(pokemon_id=pokemon.id).first()
            note_text = note_entry.note_text if note_entry else ''

            # Append extended data
            extended_pokemon_list.append({
                'id': pokemon.id,
                'dex_number': pokemon.dex_number,  # Include dex_number if needed
                'name': pokemon.name,
                'type': pokemon.type,
                'image_url': pokemon.image_url,
                'brady_living_dex': brady_living_dex,
                'brady_lucky_dex': brady_lucky_dex,
                'matt_have': matt_have,
                'matt_lucky': matt_lucky,
                'need_on_ipad': need_on_ipad,
                'ipad_lucky_dex': ipad_lucky_dex,
                'note_text': note_text,
                'legendary': legendary,
                'mythical': mythical,
                'ultra_beast': ultra_beast,
            })

        return render_template('pokemon.html', pokemon_list=extended_pokemon_list)
    
    @app.route('/pogo/save-all-changes', methods=['POST'])
    @requires_auth
    def save_all_changes():
        data = request.get_json()

        # Ensure data is received correctly
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # === Process Notes Data ===
        notes = data.get('notes', [])
        for note in notes:
            pokemon_id = note.get('pokemon_id')
            note_text = note.get('note')
            if pokemon_id:
                existing_note = Note.query.filter_by(pokemon_id=pokemon_id).first()
                if existing_note:
                    existing_note.note_text = note_text  # Update the existing note
                else:
                    new_note = Note(pokemon_id=pokemon_id, note_text=note_text)
                    db.session.add(new_note)  # Add a new note if none exists

        # === Process Checkbox Data for Pokémon and Shiny Pokémon ===
        for checkbox in data.get('checkboxes', []):
            entity_id = checkbox.get('shiny_id') or checkbox.get('pokemon_id')  # Adjusted key usage here
            checkbox_type = checkbox.get('type')
            checked_value = checkbox.get('value') == 'Yes'

            # Process checkboxes for Shiny Pokémon if type starts with "shiny_"
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

                    # Save the change to the database
                    db.session.add(shiny_pokemon)

            # Process checkboxes for normal Pokémon
            else:
                pokemon = Pokemon.query.filter_by(id=entity_id).first()
                if pokemon:
                    if checkbox_type == 'matt_lucky':
                        pokemon.user_2_lucky = checked_value
                    elif checkbox_type == 'matt_have':
                        pokemon.user_2_living_dex = checked_value
                    elif checkbox_type == 'ipad_lucky':
                        pokemon.user_0_lucky = checked_value

                    # Save the change to the database
                    db.session.add(pokemon)

        # === Commit All Changes to the Database ===
        try:
            db.session.commit()
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

    # Specials page route
    @app.route('/pogo/specials')
    def specials():
        specials_data = SpecialsPokemon.query.all()
        return render_template('specials.html', specials_data=specials_data)

    # Costumes page route
    @app.route('/pogo/costumes')
    def costumes():
        costumes_data = Costume.query.all()
        return render_template('costumes.html', costumes_data=costumes_data)

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

            # Initialize as 'No' for both columns
            shadow_living_dex = 'No'
            purified_living_dex = 'No'

            # Query for shadow living dex (lucky = 0, favorite = 0, shadow_purified = 1)
            shadow_entries = PokeGenieEntry.query.filter_by(
                pokemon_number=dex_number, lucky=0, favorite=0, shadow_purified=1
            ).all()

            if shadow_entries:
                shadow_living_dex = 'Yes'  # Mark as 'Yes' if any entry matches the condition

            # Query for purified living dex (lucky = 0, favorite = 0, shadow_purified = 2)
            purified_entries = PokeGenieEntry.query.filter_by(
                pokemon_number=dex_number, lucky=0, favorite=0, shadow_purified=2
            ).all()

            if purified_entries:
                purified_living_dex = 'Yes'  # Mark as 'Yes' if any entry matches the condition

            # Append the updated data for display
            updated_rocket_data.append({
                'dex_number': rocket_pokemon.dex_number,
                'name': rocket_pokemon.name,
                'method': rocket_pokemon.method,
                'shadow_living_dex': shadow_living_dex,
                'purified_living_dex': purified_living_dex
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
        redirect_url = url_for('authorize', _external=True)
        print(f"Google OAuth redirect URL: {redirect_url}")  # Log the redirect URI being used
        return google.authorize_redirect(redirect_url)

        next_url = request.args.get('next', url_for('info_page'))
        session['next_url'] = next_url
        return google.authorize_redirect(redirect_uri=url_for('authorize', _external=True))

    # OAuth2 callback route after user authenticates
    @app.route('/pogo/oauth2callback')
    def authorize():
        token = google.authorize_access_token()
        if token is None:
            return "Authorization failed.", 400
        session['user'] = token  # Save user token in session

        # Get the next URL and edit mode from the session
        next_url = session.pop('next_url', url_for('info_page'))
        edit_mode = session.pop('edit_mode', False)

        # Append 'edit=true' if in edit mode and it's not already in the URL
        if edit_mode and 'edit=true' not in next_url:
            separator = '&' if '?' in next_url else '?'
            next_url += f"{separator}edit=true"
        return redirect(next_url)

    # Logout route to clear the session
    @app.route('/pogo/logout')
    def logout():
        # Clear all session data related to the user
        session.clear()
        # Redirect to the homepage or a logout confirmation page instead of login
        return redirect(url_for('info_page'))  # Replace 'info_page' with your homepage or landing page

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

    # Update Specials data route
    @app.route('/pogo/update-specials', methods=['POST'])
    @requires_auth
    def update_specials():
        from scripts.update_specials import fetch_and_update_specials  # Move import here
        with app.app_context():
            fetch_and_update_specials()
        return redirect(url_for('specials'))

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