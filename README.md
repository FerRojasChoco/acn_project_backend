# ACN Project - Backend

![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=for-the-badge&logo=fastapi)
![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI%20Server-ffbe0b?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql)

Backend system for the Advanced Computer Networks project programming competition platform.

## How to run the project

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL database

### Installation & Running

1. **Clone and setup**:
```bash
git clone https://github.com/FerRojasChoco/acn_project_backend
cd acn_project  
```

2. **Install dependencies with uv**:
```bash
uv sync
```

3. **Setup environment**:

> **Note:** PostgreSQL uses port **5432** by default.  
> However, if your system is using a different port, you can check the actual port with:
> ```bash
> sudo ss -tnlp | grep postgres
> ```
> or:
> ```bash
> psql -U <user> -c "SHOW port;"
> ```

```bash
# Create .env file with (url is just an example ofc):
echo 'DATABASE_URL="postgresql://<user>:<pw>@localhost:5432/acn_db"' > .env
echo 'SECRET_KEY="lekajak"' >> .env
echo 'ALGORITHM="HS256"' >> .env
```

4. **Run the server**:
```bash
uv run uvicorn app.main:app --reload
```

5. **Access the API**:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs


## Project folder structure (planned, subject to changes)

```bash
acn_project/
├── app/
│   ├── main.py                 
│   ├── core/
│   │   ├── config.py           
│   │   ├── security.py         
│   │   └── database.py         
│   ├── models/
│   │   └── __init__.py         
│   └── api/
│       └── endpoints/
│           ├── auth.py         
│           ├── problems.py     
│           └── submissions.py  
├── scripts/
│   └── init_db.py             
├── .env                       
└── pyproject.toml            
```

## Database Models
- **Users**: Competition participants (pre-created: user_a, user_b, user_c)
- **Problems**: coding problems (included descrp, test cases path, etc)
- **Submissions**: user code with status

## Task checklist  
- Implemented: initial database setup with automatic db init, user auth, password hashing/security, API structure  
- TODO: add websocket for real time thingys, leaderboard, submission creation/management endpoints?
