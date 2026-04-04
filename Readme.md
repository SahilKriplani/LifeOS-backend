# ⚙️ LifeOS — Backend

> Scalable FastAPI REST API powering the LifeOS personal productivity platform.

[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-9.x-4479A1?logo=mysql)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 Overview

LifeOS Backend is the REST API layer for the [LifeOS Frontend](https://github.com/sahilkriplani/lifeos-frontend). Built with FastAPI and a layered architecture (Routers → Services → Models), it handles all business logic, data persistence, and authentication for the LifeOS platform.

**Domains served:**
- 🔐 **Auth** — Register, login, logout via JWT in httpOnly cookies
- 📅 **Planner** — Task CRUD with priority levels and date-based filtering
- 📊 **DSA** — Problem logs with platform, difficulty, topic tracking and stats
- 🏋️ **Fitness** — Daily weight, calorie, and step logs with aggregated stats
- 🔥 **Streaks** — Daily check-in system with current and best streak tracking

---

## 🧰 Tech Stack

| Category | Tool | Version |
|---|---|---|
| Framework | FastAPI | Latest |
| Language | Python | 3.9+ |
| ORM | SQLAlchemy | 2.x |
| Migrations | Alembic | Latest |
| Validation | Pydantic | v2 |
| Authentication | JWT (httpOnly cookies) | — |
| Password Hashing | bcrypt | — |
| Database | MySQL | 9.x |
| Server | Uvicorn | Latest |

---

## 🏗️ Architecture

```
HTTP Request
     │
     ▼
  Routers              # Route definitions, request parsing
     │
     ▼
  Services             # Business logic, orchestration
     │
     ▼
  Models (ORM)         # SQLAlchemy models → MySQL
     │
     ▼
  MySQL 9.x
```

**Key decisions:**
- **Layered architecture** — routers never contain business logic; services never know about HTTP
- **Pydantic v2** — strict request/response schema validation with clear error messages
- **Stateless JWT auth** — tokens stored in httpOnly cookies, no server-side session
- **Alembic migrations** — all schema changes are versioned and reproducible
- **Response wrapper** — uniform `{ success, data, message }` shape across all endpoints

---

## 📁 Folder Structure

```
backend/
└── app/
    ├── main.py              # Entry point — CORS config, router registration, lifespan
    ├── config.py            # Pydantic settings from .env
    ├── database.py          # SQLAlchemy engine, session factory, Base
    │
    ├── models/              # ORM table definitions
    │   ├── user.py
    │   ├── task.py
    │   ├── dsa_log.py
    │   ├── fitness_log.py
    │   └── streak.py
    │
    ├── schemas/             # Pydantic request/response schemas
    │   ├── auth.py
    │   ├── task.py
    │   ├── dsa.py
    │   ├── fitness.py
    │   └── streak.py
    │
    ├── routers/             # Route handlers (thin — delegate to services)
    │   ├── auth.py
    │   ├── tasks.py
    │   ├── dsa.py
    │   ├── fitness.py
    │   └── streaks.py
    │
    ├── services/            # Business logic
    │   ├── auth_service.py
    │   ├── task_service.py
    │   ├── dsa_service.py
    │   ├── fitness_service.py
    │   └── streak_service.py
    │
    └── utils/
        ├── jwt.py           # Token creation, decoding, cookie helpers
        └── response.py      # Uniform response wrapper
```

---

## ⚙️ Getting Started

### Prerequisites

- Python `3.9+`
- MySQL `8+` running locally
- A database named `lifeos` already created

### Installation

```bash
git clone https://github.com/sahilkriplani/lifeos-backend.git
cd lifeos-backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Migrations

```bash
alembic upgrade head
```

### Start the Server

```bash
uvicorn app.main:app --reload
```

API base: [http://localhost:8000](http://localhost:8000)  
Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)  
ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔑 Environment Variables

Create a `.env` file in the root:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost/lifeos
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 🗃️ Database Schema

```sql
CREATE TABLE users (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  email      VARCHAR(150) UNIQUE NOT NULL,
  password   VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  user_id        INT NOT NULL,
  title          VARCHAR(255) NOT NULL,
  is_done        BOOLEAN DEFAULT FALSE,
  scheduled_date DATE NOT NULL,
  priority       ENUM('low', 'medium', 'high') DEFAULT 'medium',
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE dsa_logs (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  problem_name VARCHAR(255) NOT NULL,
  platform     ENUM('leetcode', 'codeforces', 'gfg', 'other') DEFAULT 'leetcode',
  difficulty   ENUM('easy', 'medium', 'hard') NOT NULL,
  topic        VARCHAR(100),
  solved_at    DATE NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE fitness_logs (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  user_id   INT NOT NULL,
  log_date  DATE NOT NULL,
  weight_kg DECIMAL(5,2),
  calories  INT,
  steps     INT,
  notes     TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE streaks (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  user_id          INT UNIQUE NOT NULL,
  current_streak   INT DEFAULT 0,
  best_streak      INT DEFAULT 0,
  last_active_date DATE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

> Schema is managed via Alembic. Do not alter tables manually in production.

---

## 🔌 API Reference

Base URL: `/api/v1`

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Create new account |
| `POST` | `/auth/login` | Login, sets httpOnly cookie |
| `POST` | `/auth/logout` | Clears auth cookie |
| `GET` | `/auth/me` | Get current user from cookie |

### Tasks (Planner)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/tasks?date=YYYY-MM-DD` | Fetch tasks for a date |
| `POST` | `/tasks` | Create a task |
| `PATCH` | `/tasks/:id` | Update task (title, done, priority) |
| `DELETE` | `/tasks/:id` | Delete a task |

### DSA
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dsa/logs?from=&to=` | Fetch logs in date range |
| `POST` | `/dsa/logs` | Log a solved problem |
| `GET` | `/dsa/stats` | Aggregated stats (by topic, difficulty) |
| `DELETE` | `/dsa/logs/:id` | Delete a log entry |

### Fitness
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/fitness/logs?from=&to=` | Fetch logs in date range |
| `POST` | `/fitness/logs` | Add a daily fitness log |
| `PATCH` | `/fitness/logs/:id` | Update a fitness log |
| `GET` | `/fitness/stats` | Aggregated fitness stats |

### Streaks
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/streaks/me` | Get current and best streak |
| `POST` | `/streaks/checkin` | Record today's activity |

All responses follow the shape:
```json
{
  "success": true,
  "data": { ... },
  "message": "OK"
}
```

---

## 🔐 Authentication

- On login, a signed JWT is stored as an httpOnly, Secure, SameSite=Lax cookie
- All protected routes use a `get_current_user` dependency that decodes the cookie
- Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 1440 = 24 hours)
- Passwords are hashed with bcrypt before storage — plaintext is never persisted

---

## 📌 Common Commands

```bash
# Run dev server
uvicorn app.main:app --reload

# Create a new migration
alembic revision --autogenerate -m "describe change"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current migration state
alembic current
```

---

## 🗺️ Roadmap

- [ ] Phase 7 — Core API setup (auth, tasks, DSA, fitness, streaks)
- [ ] Phase 8 — Auth with httpOnly JWT cookies
- [ ] Phase 9 — Stats aggregation endpoints
- [ ] Phase 10 — Deployment (Railway / Render / EC2)

---

## 🧠 Engineering Principles

- **Thin routers** — route handlers only parse requests and return responses
- **Service layer** — all business logic lives in services, independently testable
- **Fail fast** — Pydantic v2 validates at the boundary; bad data never reaches the DB
- **Secure by default** — httpOnly cookies, bcrypt, no sensitive data in responses
- **Reproducible** — Alembic migrations ensure schema consistency across environments

---

## 🔗 Related

- [LifeOS Frontend](https://github.com/sahilkriplani/lifeos-frontend) — Next.js 16 + React 19 dashboard

---

## 👤 Author

**Sahil Kriplani** — Full-Stack Developer, Ahmedabad 🇮🇳  
GitHub: [@sahilkriplani](https://github.com/sahilkriplani)

> *"Clean APIs. Scalable systems. Production mindset."*