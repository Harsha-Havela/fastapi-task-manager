# FastAPI Task Manager

A full-stack Task Manager application built with **FastAPI** (backend) and **Jinja2 templates** (frontend).

## 🚀 Live Demo

- **Live Application:** https://fastapi-task-manager-production-366e.up.railway.app
- **API Documentation (Swagger):** https://fastapi-task-manager-production-366e.up.railway.app/docs
- **GitHub Repository:** https://github.com/Harsha-Havela/fastapi-task-manager

---

## 📋 Project Overview

| Component | Technology                          |
|-----------|-------------------------------------|
| Backend   | FastAPI, SQLAlchemy, SQLite/PostgreSQL |
| Authentication | JWT (python-jose), bcrypt (passlib) |
| Frontend  | Jinja2 Templates + HTML/CSS/JavaScript |
| Testing   | pytest + httpx TestClient            |
| Deployment | Railway + Docker                     |

### ✨ Features

- ✅ User registration & login with JWT authentication
- ✅ Full CRUD operations for tasks (create, read, update, delete)
- ✅ Mark tasks as completed/incomplete
- ✅ Filter tasks by completion status (`?completed=true/false`)
- ✅ Pagination support (`?page=1&page_size=10`)
- ✅ User isolation (users can only access their own tasks)
- ✅ Interactive Swagger UI at `/docs`
- ✅ Responsive modern UI with glassmorphism design
- ✅ Auto-redirect after registration with username pre-fill

---

## 📁 Project Structure

```
task-manager/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py          # Authentication dependencies
│   │   │   └── routes/
│   │   │       ├── auth.py      # POST /register, POST /login
│   │   │       └── tasks.py     # Task CRUD endpoints
│   │   ├── core/
│   │   │   ├── config.py        # Application settings
│   │   │   └── security.py      # JWT + bcrypt utilities
│   │   ├── db/
│   │   │   └── session.py       # SQLAlchemy database session
│   │   ├── models/
│   │   │   ├── user.py          # User SQLAlchemy model
│   │   │   └── task.py          # Task SQLAlchemy model
│   │   ├── schemas/
│   │   │   ├── user.py          # User Pydantic schemas
│   │   │   └── task.py          # Task Pydantic schemas
│   │   ├── templates/
│   │   │   └── index.html       # Frontend Jinja2 template
│   │   └── main.py              # FastAPI application entry point
│   ├── tests/
│   │   ├── conftest.py          # Test configuration
│   │   ├── test_auth.py         # Authentication tests
│   │   └── test_tasks.py        # Task management tests
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Docker configuration
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── docker-compose.yml           # Docker Compose configuration
└── README.md                    # Project documentation
```

---

## 🔧 Environment Variables

Copy `.env.example` to `backend/.env` and configure the following variables:

| Variable                    | Default                        | Description                          |
|-----------------------------|--------------------------------|--------------------------------------|
| `SECRET_KEY`                | `your-secret-key-here`         | JWT signing secret (use a secure random string) |
| `ALGORITHM`                 | `HS256`                        | JWT algorithm                        |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` (24 hours)            | JWT token lifetime                   |
| `DATABASE_URL`              | `sqlite:///./taskmanager.db`   | Database connection URL              |

**Generate a secure secret key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🚀 Running Locally

### Option 1: Python Virtual Environment

```bash
# 1. Clone the repository
git clone https://github.com/Harsha-Havela/fastapi-task-manager.git
cd task-manager/backend

# 2. Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp ../.env.example .env
# Edit .env and set your SECRET_KEY

# 5. Start the development server
uvicorn app.main:app --reload --port 8000
```

**Access the application:**
- 🌐 **Web App:** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs

### Option 2: Docker Compose

```bash
# 1. Clone and navigate to project
git clone https://github.com/Harsha-Havela/fastapi-task-manager.git
cd task-manager

# 2. Set up environment variables
cp .env.example backend/.env
# Edit backend/.env with your configuration

# 3. Build and start with Docker
docker compose up --build
```

**Access at:** http://localhost:8000

---

## 🧪 Running Tests

```bash
cd task-manager/backend

# Install test dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app tests/
```

---

## 📡 API Endpoints

### Authentication Endpoints

| Method | Endpoint    | Description              | Authentication |
|--------|-------------|--------------------------|----------------|
| POST   | `/register` | Register a new user      | None           |
| POST   | `/login`    | Login and get JWT token  | None           |

### Task Management Endpoints

| Method | Endpoint       | Description                        | Authentication |
|--------|----------------|------------------------------------|----------------|
| POST   | `/tasks`       | Create a new task                  | JWT Required   |
| GET    | `/tasks`       | List tasks (with filtering/pagination) | JWT Required   |
| GET    | `/tasks/{id}`  | Get a specific task by ID          | JWT Required   |
| PUT    | `/tasks/{id}`  | Update task (title/description/completed) | JWT Required   |
| DELETE | `/tasks/{id}`  | Delete a task by ID                | JWT Required   |

### Query Parameters for `GET /tasks`

| Parameter   | Type    | Description                          | Default |
|-------------|---------|--------------------------------------|---------|
| `completed` | boolean | Filter by completion status          | None    |
| `page`      | integer | Page number for pagination           | 1       |
| `page_size` | integer | Number of items per page (max: 100)  | 10      |

**Example requests:**
```bash
# Get all tasks
GET /tasks

# Get completed tasks only
GET /tasks?completed=true

# Get pending tasks with pagination
GET /tasks?completed=false&page=2&page_size=5
```

---

## 🌐 Deployment

This application is deployed on **Railway** with the following configuration:

### Railway Deployment Steps:

1. **Connect GitHub Repository** to Railway
2. **Set Root Directory** to `backend`
3. **Configure Environment Variables** in Railway dashboard
4. **Automatic Deployment** on every push to main branch

### Environment Variables (Production):
```
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@host:port/database
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256
```

### Alternative Deployment Platforms:

**Render:**
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Vercel:**
- Use `vercel.json` configuration for serverless deployment

---

## 🏗️ Technical Implementation

### Backend Architecture:
- **FastAPI** for REST API with automatic OpenAPI documentation
- **SQLAlchemy** ORM for database operations
- **Pydantic** for data validation and serialization
- **JWT** for stateless authentication
- **bcrypt** for secure password hashing
- **Jinja2** for server-side template rendering

### Frontend Features:
- **Single Page Application** with dynamic content loading
- **JWT token management** with localStorage
- **Responsive design** with modern glassmorphism UI
- **Form validation** and error handling
- **Auto-redirect** functionality after registration

### Security Features:
- Password hashing with bcrypt
- JWT token-based authentication
- User isolation (users can only access their own data)
- Input validation with Pydantic
- CORS configuration for cross-origin requests

---

## 🎯 Internship Requirements Checklist

### ✅ Core Requirements:
- [x] FastAPI backend with REST API
- [x] User registration and login
- [x] JWT-based authentication
- [x] Password hashing (bcrypt)
- [x] Task CRUD operations
- [x] User task isolation
- [x] SQLAlchemy database integration
- [x] Pydantic models
- [x] Proper HTTP status codes
- [x] Error handling
- [x] Clean folder structure
- [x] Basic frontend interface
- [x] GitHub repository
- [x] Live deployment
- [x] Environment variables
- [x] README documentation

### 🏆 Bonus Features:
- [x] Pagination for tasks
- [x] Task filtering by completion status
- [x] Test cases with pytest
- [x] Dockerfile for containerization
- [x] Responsive UI design
- [x] Proper frontend/backend separation

---

## 👨‍💻 Author

**Harsha Havela**
- GitHub: [@Harsha-Havela](https://github.com/Harsha-Havela)
- Project: [FastAPI Task Manager](https://github.com/Harsha-Havela/fastapi-task-manager)

---

## 📄 License

This project is created for internship evaluation purposes.
