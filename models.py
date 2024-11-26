from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)

    # Relationship to OwnedPokemon
    owned_pokemon = db.relationship('OwnedPokemon', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.name}>"

# Pokémon Model
class Pokemon(db.Model):
    __tablename__ = 'pokemon'
    id = db.Column(db.Integer, primary_key=True)
    dex_number = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(50), nullable=True)  # Hidden in HTML
    shiny_released = db.Column(db.Boolean, default=False, nullable=True)  # Hidden in HTML
    notes = db.Column(db.Text, default="", nullable=True)  # Plans to change notes to save here
    
    # Ownership tracking fields
    brady_living_dex = db.Column(db.Boolean, default=False, nullable=True)
    brady_shiny = db.Column(db.Boolean, default=False, nullable=True)
    brady_lucky = db.Column(db.Boolean, default=False, nullable=True)
    matt_living_dex = db.Column(db.Boolean, default=False, nullable=True)
    matt_shiny = db.Column(db.Boolean, default=False, nullable=True)
    matt_lucky = db.Column(db.Boolean, default=False, nullable=True)
    ipad_living_dex = db.Column(db.Boolean, default=True, nullable=True)
    ipad_shiny = db.Column(db.Boolean, default=False, nullable=True)
    ipad_lucky = db.Column(db.Boolean, default=False, nullable=True)
    
    def __repr__(self):
        return f"<Pokemon {self.dex_number} - {self.name}>"

# Association Table for User-Pokemon Ownership
class OwnedPokemon(db.Model):
    __tablename__ = 'owned_pokemon'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), nullable=False)
    have_living_dex = db.Column(db.Boolean, default=False)
    lucky_dex = db.Column(db.Boolean, default=False)
    need_on_ipad = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<OwnedPokemon User {self.user_id} - Pokemon {self.pokemon_id}>"

# Poke Genie Entry Model
class PokeGenieEntry(db.Model):
    __tablename__ = 'poke_genie'
    index = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    form = db.Column(db.String(50))
    pokemon_number = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    cp = db.Column(db.Integer)
    hp = db.Column(db.Integer)
    atk_iv = db.Column(db.Integer)
    def_iv = db.Column(db.Integer)
    sta_iv = db.Column(db.Integer)
    iv_avg = db.Column(db.Float)
    level_min = db.Column(db.Float)
    level_max = db.Column(db.Float)
    quick_move = db.Column(db.String(50))
    charge_move = db.Column(db.String(50))
    charge_move_2 = db.Column(db.String(50))
    scan_date = db.Column(db.String(50))
    original_scan_date = db.Column(db.String(50))
    catch_date = db.Column(db.String(50))
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    lucky = db.Column(db.Integer)  # 0 or 1
    shadow_purified = db.Column(db.Integer)  # 0: Regular, 1: Shadow, 2: Purified
    favorite = db.Column(db.Integer)  # 0-5
    dust = db.Column(db.Integer)
    rank_g_pct = db.Column(db.Float)
    rank_g_num = db.Column(db.Integer)
    stat_prod_g = db.Column(db.Float)
    dust_cost_g = db.Column(db.Integer)
    candy_cost_g = db.Column(db.Integer)
    name_g = db.Column(db.String(50))
    form_g = db.Column(db.String(50))
    sha_pur_g = db.Column(db.Integer)
    rank_u_pct = db.Column(db.Float)
    rank_u_num = db.Column(db.Integer)
    stat_prod_u = db.Column(db.Float)
    dust_cost_u = db.Column(db.Integer)
    candy_cost_u = db.Column(db.Integer)
    name_u = db.Column(db.String(50))
    form_u = db.Column(db.String(50))
    sha_pur_u = db.Column(db.Integer)
    rank_l_pct = db.Column(db.Float)
    rank_l_num = db.Column(db.Integer)
    stat_prod_l = db.Column(db.Float)
    dust_cost_l = db.Column(db.Integer)
    candy_cost_l = db.Column(db.Integer)
    name_l = db.Column(db.String(50))
    form_l = db.Column(db.String(50))
    sha_pur_l = db.Column(db.Integer)
    marked_for_pvp = db.Column(db.Integer)  # 0 or 1

    def __repr__(self):
        return f"<PokeGenieEntry {self.index} - {self.name}>"

# Shiny Pokémon Model
class ShinyPokemon(db.Model):
    __tablename__ = 'shinies'
    id = db.Column(db.Integer, primary_key=True)
    dex_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    form = db.Column(db.String(100), nullable=True)  # New column for the form
    method = db.Column(db.String(255))

    # Ownership tracking fields for Brady and Matt
    brady_own = db.Column(db.Boolean, default=False)
    brady_lucky = db.Column(db.Boolean, default=False)
    matt_own = db.Column(db.Boolean, default=False)
    matt_lucky = db.Column(db.Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('dex_number', 'name', 'form', name='_dex_name_form_uc'),
    )

    def __repr__(self):
        return f"<ShinyPokemon {self.dex_number} - {self.name} ({self.form})>"

# Costume Pokémon Model
class Costume(db.Model):
    __tablename__ = 'costumes'
    id = db.Column(db.Integer, primary_key=True)
    dex_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    costume = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    shiny_image_url = db.Column(db.String(255), nullable=True)

    # Ownership tracking fields for Brady and Matt
    brady_own = db.Column(db.Boolean, default=False)
    brady_shiny = db.Column(db.Boolean, default=False)
    matt_own = db.Column(db.Boolean, default=False)
    matt_shiny = db.Column(db.Boolean, default=False)

    # Unique Constraint for (dex_number, name, costume) combination
    __table_args__ = (
        db.UniqueConstraint('dex_number', 'name', 'costume', name='_dex_name_costume_uc'),
    )

    def __repr__(self):
        return f"<Costume {self.dex_number} - {self.name} ({self.costume})>"

# Form Pokémon Model
class Form(db.Model):
    __tablename__ = 'forms'
    id = db.Column(db.Integer, primary_key=True)
    dex_number = db.Column(db.String(10))
    name = db.Column(db.String(100))
    form = db.Column(db.String(100))

    def __repr__(self):
        return f"<Form {self.dex_number} - {self.name} ({self.form})>"

# Rocket Pokémon Model
class Rocket(db.Model):
    __tablename__ = 'rocket'
    id = db.Column(db.Integer, primary_key=True)
    dex_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    method = db.Column(db.String(255), nullable=True)

    # Ownership tracking fields for Brady and Matt
    brady_shadow = db.Column(db.Boolean, default=False)  # Formerly shadow_living_dex
    brady_purified = db.Column(db.Boolean, default=False)  # Formerly purified_living_dex
    matt_shadow = db.Column(db.Boolean, default=False)  # New column for Matt's shadow Pokémon
    matt_purified = db.Column(db.Boolean, default=False)  # New column for Matt's purified Pokémon

    __table_args__ = (
        db.UniqueConstraint('dex_number', 'name', name='_dex_name_uc'),
    )

    def __repr__(self):
        return f"<Rocket {self.dex_number} - {self.name}>"

# All Pokémon Model
class AllPokemon(db.Model):
    __tablename__ = 'all_pokemon'
    id = db.Column(db.Integer, primary_key=True)
    dex_number = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100))
    link = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(100))  # Superscript category like "Starter", "Legendary", etc.
    generation = db.Column(db.Integer)
    released = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<AllPokemon {self.dex_number} - {self.name}>"

# Note Model
class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    pokemon_id = db.Column(db.Integer)
    note_text = db.Column(db.Text)

    def __repr__(self):
        return f"<Note for Pokémon ID {self.pokemon_id}>"