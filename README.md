# Task Manager

A full-stack Task Manager application built with **FastAPI** (backend) and plain **HTML/CSS/JavaScript** (frontend).

## Live Demo

> Add your deployment links here after deploying.

- **Frontend / App:** `https://your-app.onrender.com`
- **API Docs (Swagger):** `https://your-app.onrender.com/docs`

---

## Project Overview

| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | FastAPI, SQLAlchemy, SQLite/Postgres |
| Auth     | JWT (python-jose), bcrypt (passlib) |
| Frontend | Plain HTML + CSS + JavaScript        |
| Tests    | pytest + httpx TestClient            |
| Deploy   | Docker / Render / Railway            |

### Features

- User registration & login with JWT authentication
- Full CRUD for tasks (create, read, update, delete)
- Mark tasks as completed
- Filter tasks by completion status (`?completed=true/false`)
- Pagination (`?page=1&page_size=10`)
- Users can only access their own tasks
- Interactive Swagger UI at `/docs`

---

## Folder Structure

```
task-manager/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py          # Auth dependency
│   │   │   └── routes/
│   │   │       ├── auth.py      # /register, /login
│   │   │       └── tasks.py     # /tasks CRUD
│   │   ├── core/
│   │   │   ├── config.py        # Settings (pydantic-settings)
│   │   │   └── security.py      # JWT + bcrypt helpers
│   │   ├── db/
│   │   │   └── session.py       # SQLAlchemy engine & session
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── task.py
│   │   ├── schemas/
│   │   │   ├── user.py          # Pydantic schemas
│   │   │   └── task.py
│   │   └── main.py              # FastAPI app entry point
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   └── test_tasks.py
│   ├── requirements.txt
│   ├── pytest.ini
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Environment Variables

Copy `.env.example` to `.env` inside the `backend/` folder and fill in your values.

| Variable                    | Default                        | Description                          |
|-----------------------------|--------------------------------|--------------------------------------|
| `SECRET_KEY`                | `change-me-in-production`      | JWT signing secret (use a long random string) |
| `ALGORITHM`                 | `HS256`                        | JWT algorithm                        |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` (24 h)               | Token lifetime                       |
| `DATABASE_URL`              | `sqlite:///./taskmanager.db`   | SQLAlchemy database URL              |

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Running Locally

### Option 1 – Python virtual environment

```bash
# 1. Clone the repo
git clone https://github.com/your-username/task-manager.git
cd task-manager/backend

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp ../.env.example .env
# Edit .env and set SECRET_KEY

# 5. Start the server
uvicorn app.main:app --reload --port 8000
```

Open your browser at:
- App UI: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

### Option 2 – Docker Compose

```bash
cd task-manager

# Copy and edit the env file
cp .env.example backend/.env

# Build and start
docker compose up --build
```

App will be available at http://localhost:8000.

---

## Running Tests

```bash
cd task-manager/backend
pytest -v
```

---

## API Endpoints

### Authentication

| Method | Path        | Description              | Auth required |
|--------|-------------|--------------------------|---------------|
| POST   | `/register` | Register a new user      | No            |
| POST   | `/login`    | Login, returns JWT token | No            |

### Tasks

| Method | Path           | Description                        | Auth required |
|--------|----------------|------------------------------------|---------------|
| POST   | `/tasks`       | Create a task                      | Yes           |
| GET    | `/tasks`       | List tasks (filter + pagination)   | Yes           |
| GET    | `/tasks/{id}`  | Get a single task                  | Yes           |
| PUT    | `/tasks/{id}`  | Update task (title/desc/completed) | Yes           |
| DELETE | `/tasks/{id}`  | Delete a task                      | Yes           |

**Query parameters for `GET /tasks`:**

| Param       | Type    | Description                          |
|-------------|---------|--------------------------------------|
| `completed` | boolean | Filter by completion (`true`/`false`) |
| `page`      | int     | Page number (default: 1)             |
| `page_size` | int     | Items per page (default: 10, max: 100) |

---

## Deployment (Render)

1. Push the repo to GitHub.
2. Create a new **Web Service** on [Render](https://render.com).
3. Set **Root Directory** to `backend`.
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (`SECRET_KEY`, `DATABASE_URL`, etc.) in the Render dashboard.
7. For the frontend, Render will serve it automatically via FastAPI's static file mount.

> For a persistent database in production, use a PostgreSQL add-on and set `DATABASE_URL` accordingly.
