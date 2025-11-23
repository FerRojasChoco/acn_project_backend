from sqlmodel import Session, select
from app.core.database import engine
from app.models import User
from app.core.security import get_password_hash


def create_initial_users():
    with Session(engine) as session:
        existing_user = session.exec(select(User)).first()

        if existing_user:
            print("users already exists, skipping user creation")
            return

        users_data = [
            {"username": "user_a", "password": "a1234"},
            {"username": "user_b", "password": "b1234"},
            {"username": "user_c", "password": "c1234"},
        ]

        for user_data in users_data:
            hashed_password = get_password_hash(user_data["password"])
            user = User(username=user_data["username"], password=hashed_password)
            session.add(user)

        session.commit()
        print("users successfully created")

if __name__ == "__main__":
    create_initial_users()
