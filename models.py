from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Pokémon Model
class Pokemon(db.Model):
    __tablename__ = 'pokemon'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))
    image_url = db.Column(db.String(255))

    def __repr__(self):
        return f"<Pokemon {self.id} - {self.name}>"

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
    dex_number = db.Column(db.Integer)
    name = db.Column(db.String(100))
    method = db.Column(db.String(255))

    def __repr__(self):
        return f"<ShinyPokemon {self.dex_number} - {self.name}>"

# Specials Pokémon Model
class SpecialsPokemon(db.Model):
    __tablename__ = 'specials'
    id = db.Column(db.Integer, primary_key=True)
    dex_number = db.Column(db.Integer)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))

    def __repr__(self):
        return f"<SpecialsPokemon {self.dex_number} - {self.name} ({self.type})>"

# Costume Model
class Costume(db.Model):
    __tablename__ = 'costumes'
    id = db.Column(db.Integer, primary_key=True)
    dex_number = db.Column(db.Integer)
    name = db.Column(db.String(100))
    costume = db.Column(db.String(100))
    first_appearance = db.Column(db.String(255))

    def __repr__(self):
        return f"<Costume {self.dex_number} - {self.name} ({self.costume})>"

# Form Model
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
    dex_number = db.Column(db.Integer)
    name = db.Column(db.String(100))
    method = db.Column(db.String(255))

    def __repr__(self):
        return f"<Rocket {self.dex_number} - {self.name}>"

# Note Model
class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    pokemon_id = db.Column(db.Integer)
    note_text = db.Column(db.Text)

    def __repr__(self):
        return f"<Note for Pokémon ID {self.pokemon_id}>"
