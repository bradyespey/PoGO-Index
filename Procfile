# Procfile for Heroku to manage local development, production, and auto-migrations.

# The release phase to automatically run database migrations on Heroku
release: flask db upgrade

# Production web process, use Gunicorn to serve your Flask app
web: gunicorn app:app

# Local development environment command (ignore this in production)
# Use flask run for local testing
dev: flask run --host=0.0.0.0 --port=5000