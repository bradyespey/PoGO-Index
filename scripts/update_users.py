# scripts/update_users.py

import sys
from pathlib import Path

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Importing the app and db for database management
from app import app, db
from models import User

def create_users():
    """Populate the users table with initial data for Brady, Matt, and iPad."""
    with app.app_context():
        # Define the users
        users = [
            {"id": 1, "name": "Brady", "email": "baespey@gmail.com"},
            {"id": 2, "name": "Matt", "email": "mtodaatt@gmail.com"},
            {"id": 0, "name": "iPad", "email": None},  # iPad doesn't have an email
        ]

        # Insert or update users
        for user_data in users:
            user = User.query.filter_by(id=user_data['id']).first()
            if user:
                # Update existing user
                user.name = user_data['name']
                user.email = user_data['email']
                print(f"Updated user: {user.name}")
            else:
                # Create new user
                new_user = User(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                )
                db.session.add(new_user)
                print(f"Added new user: {new_user.name}")

        db.session.commit()
        print("Users table populated successfully.")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        create_users()