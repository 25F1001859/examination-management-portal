import os
import getpass
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User


app = create_app()

def initialize_database():
    with app.app_context():

        db.create_all()
        admin = User.query.filter_by(role="admin").first()

        if admin:
            print("Admin account already exists.")
            return

        print("\nCreate the initial Admin account")

        name = os.getenv("ADMIN_NAME", "System Admin")
        email = os.getenv("ADMIN_EMAIL")

        if not email:
            email = input("Admin email: ").strip()

        if User.query.filter_by(email=email).first():
            print("This email is already registered.")
            return

        password = os.getenv("ADMIN_PASSWORD")

        if not password:
            password = getpass.getpass("Admin password: ")
            confirm = getpass.getpass("Confirm password: ")

            if password != confirm:
                print("Passwords do not match.")
                return

        if len(password) < 8:
            print("Password must be at least 8 characters.")
            return

        admin = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="admin",
            status="active"
        )

        db.session.add(admin)
        db.session.commit()

        print("\nDatabase initialized successfully!")
        print(f"Admin email: {email}")


if __name__ == "__main__":
    initialize_database()
