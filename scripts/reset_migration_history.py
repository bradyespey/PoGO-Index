# scripts/reset_migration_history.py

import sys
from pathlib import Path

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app import app, db
from sqlalchemy import text

# Ensure actions are within the application context
with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))
        print("Cleared alembic_version table.")
