from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from enum import Enum

class SubmissionStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    WRONG_ANS = "WRONG_ANS"
    RUNTIME_ERR = "RUNTIME_ERR"
    INTERNAL_ERR = "INTERNAL_ERR"

class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password: str = Field(nullable=False)
    __tablename__ = "users"

class Problem(SQLModel, table=True):
    problem_id: Optional[int] = Field(default=None, primary_key=True)
    problem_title: str = Field(index=True, unique=True, nullable=False)
    problem_description: str = Field(nullable=False)
    starter_code: str = Field(nullable=False)
    testcases_path: str = Field(nullable=False)
    __tablename__ = "problems"  

class Submission(SQLModel, table=True):
    submission_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id", index=True, nullable=False)  
    problem_id: int = Field(foreign_key="problems.problem_id", index=True, nullable=False)  
    code: str = Field(nullable=False)
    status: SubmissionStatus = Field(default=SubmissionStatus.PENDING, nullable=False)
    submitted_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    __tablename__ = "submissions"
