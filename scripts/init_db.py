from sqlmodel import Session, select
from app.core.database import engine
from app.models import User, Problem
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


def create_initial_problems():
    """Initialize problems in the database"""
    with Session(engine) as session:
        # Check if problems already exist
        existing_problem = session.exec(select(Problem)).first()

        if existing_problem:
            print("problems already exist, skipping problem creation")
            return

        problems_data = [
            {
                "problem_title": "Fibonacci Sequence",
                "problem_description": """Create a function solve(n) which receives an index n and returns the nth Fibonacci number.

The Fibonacci sequence is defined as:
- F(0) = 0
- F(1) = 1
- F(n) = F(n-1) + F(n-2) for n > 1

For example:
- solve(0) should return 0
- solve(1) should return 1
- solve(5) should return 5
- solve(10) should return 55

Expected time complexity: O(log(n))
Expected space complexity: O(1)

Hint: Consider using matrix exponentiation for optimal performance.""",
                "starter_code": """def solve(n):
    return 1""",
                "testcases_path": "problem1/input/",
            },
            {
                "problem_title": "Is it prime?",
                "problem_description": """Create a function solve(n) which receives a number n and returns True if the number is prime, False otherwise.

A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.

For example:
- solve(2) should return True
- solve(3) should return True
- solve(4) should return False
- solve(17) should return True
- solve(100) should return False

Expected time complexity: O(sqrt(n))
Expected space complexity: O(1)

Hint: You only need to check divisibility up to the square root of n.""",
                "starter_code": """def solve(n):
    return True""",
                "testcases_path": "problem2/input/",
                "max_score": 100
            },
        ]

        for problem_data in problems_data:
            problem = Problem(**problem_data)
            session.add(problem)

        session.commit()
        print("problems successfully created")


if __name__ == "__main__":
    create_initial_users()
    create_initial_problems()