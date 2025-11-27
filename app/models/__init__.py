from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SubmissionStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    WRONG_ANS = "WRONG_ANS"
    MEM_LIMIT = "MLE"
    TIME_LIMIT = "TLE"  # Value is "TLE", not "TIME_LIMIT"
    RUNTIME_ERR = "RUNTIME_ERR"
    INTERNAL_ERR = "INTERNAL_ERR"

class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password: str = Field(nullable=False)
    __tablename__ = "users"

    submissions: List["Submission"] = Relationship(back_populates="user")
    scores: List["UserScore"] = Relationship(back_populates="user")

class Problem(SQLModel, table=True):
    problem_id: Optional[int] = Field(default=None, primary_key=True)
    problem_title: str = Field(index=True, unique=True, nullable=False)
    problem_description: str = Field(nullable=False)
    starter_code: str = Field(nullable=False)
    max_score: int = Field(default=100)
    __tablename__ = "problems"  

    submissions: List["Submission"] = Relationship(back_populates="problem")
    scores: List["UserScore"] = Relationship(back_populates="problem")

class Submission(SQLModel, table=True):
    submission_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id", index=True, nullable=False)  
    problem_id: int = Field(foreign_key="problems.problem_id", index=True, nullable=False)  
    code: str = Field(nullable=False)
    status: SubmissionStatus = Field(default=SubmissionStatus.PENDING, nullable=False)
    score: int = Field(default=0)
    result: Optional[str] = Field(default=None, nullable=True)
    submitted_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    __tablename__ = "submissions"

    user: User = Relationship(back_populates="submissions")
    problem: Problem = Relationship(back_populates="submissions")

class UserScore(SQLModel, table=True):
    user_score_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id", index=True, nullable=False)
    problem_id: int = Field(foreign_key="problems.problem_id", index=True, nullable=False)
    best_score: int = Field(default=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    __tablename__ = "user_scores"

    user: User = Relationship(back_populates="scores")
    problem: Problem = Relationship(back_populates="scores")