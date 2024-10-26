import sys
import os
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from models import db, User, Pokemon, OwnedPokemon, PokeGenieEntry, ShinyPokemon, SpecialsPokemon, Costume, Form, Rocket, Note  # Import all models
from routes import init_routes
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Flask app with static folder configuration
app = Flask(__name__, static_url_path='/static', static_folder='static')

# Add secret key for session protection (important for OAuth)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')  # Replace with a secure key in production

# Determine the environment (development or production)
ENV = os.getenv("FLASK_ENV", "production")  # Default to production if not set

# Configure the database based on environment
if ENV == "development":
    # Use SQLite for local development
    db_path = os.getenv("DATABASE_URL", "sqlite:///pogo.db")
else:
    # Use PostgreSQL for production (Heroku)
    db_path = os.getenv("DATABASE_URL")
    if db_path and db_path.startswith("postgres://"):
        db_path = db_path.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Set up database migrations
migrate = Migrate(app, db)

# OAuth configuration with dynamic redirect URI based on environment
if ENV == "development":
    redirect_uri = os.getenv('DEV_REDIRECT_URI')
else:
    redirect_uri = os.getenv('PROD_REDIRECT_URI')

# OAuth configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('OAUTH_CLIENT_ID'),
    client_secret=os.getenv('OAUTH_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    redirect_uri=redirect_uri,  # Correct redirect_uri set here
    client_kwargs={'scope': 'openid profile email'}
)

# Debug the redirect_uri being used
print(f"Redirect URI being used: {redirect_uri}")

# Debug the redirect_uri being used
print(f"Redirect URI being used: {os.getenv('REDIRECT_URIS')}")

# Ensure that OAuth environment variables are set
if not os.getenv('OAUTH_CLIENT_ID') or not os.getenv('OAUTH_CLIENT_SECRET'):
    raise ValueError("Google OAuth credentials are not set in environment variables")

# Initialize application routes
init_routes(app, google)

# Run the Flask application
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv("PORT", 5002)),  # Use PORT from environment for Heroku, default to 5002 locally
        debug=os.getenv('DEBUG', 'True').lower() == 'true'  # Toggle debug mode based on environment variable
    )