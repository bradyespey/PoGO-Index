# app.py

import os
from flask import Flask
from authlib.integrations.flask_client import OAuth
from models import db  # Import db here
from routes import init_routes
from flask_migrate import Migrate
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')

# Determine environment and set redirect_uri
env = os.getenv('FLASK_ENV', 'production')
redirect_uri = os.getenv('PROD_REDIRECT_URI') if env == 'production' else os.getenv('DEV_REDIRECT_URI')

# Configure the database URI
db_path = os.getenv("DATABASE_URL")
if env == 'production' and db_path and db_path.startswith("postgres://"):
    db_path = db_path.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Apply ProxyFix to ensure Heroku recognizes requests as HTTPS
if env == 'production':
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize the database and migrations
db.init_app(app)  # Initialize db with the app here
migrate = Migrate(app, db)

# OAuth setup with Google
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('OAUTH_CLIENT_ID'),
    client_secret=os.getenv('OAUTH_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    redirect_uri=redirect_uri,
    client_kwargs={'scope': 'openid profile email'}
)

# Debugging (uncomment to verify)
print(f"Environment: {env}")
print(f"Redirect URI being used: {redirect_uri}")

# Initialize routes
init_routes(app, google)

# Run the app
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv("PORT", 5002)),
        debug=(env == 'development')
    )
# Trigger rebuild
