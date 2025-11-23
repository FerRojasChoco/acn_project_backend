from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, create_db_and_tables

from app.api.endpoints import auth, problems, submissions

from app.models import User, Problem, Submission  
from scripts.init_db import create_initial_users  

app = FastAPI(title="ACN project")

#  note: notify Fede about this part for the front
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(problems.router, prefix="/problems", tags=["problems"])
app.include_router(submissions.router, prefix="/submissions", tags=["submissions"])

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # uncomment for creation of initial users on startup
    create_initial_users()

@app.get("/")
def read_root():
    return {"message": "ACN project API test"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
