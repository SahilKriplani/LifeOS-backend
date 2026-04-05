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
| Framework | FastAPI | 0.128.8 |
| Language | Python | 3.9+ |
| ORM | SQLAlchemy | 2.x |
| Validation | Pydantic | v2 |
| Authentication | JWT (httpOnly cookies) | python-jose 3.5.0 |
| Password Hashing | bcrypt | passlib 1.7.4 + bcrypt 4.0.1 |
| Database | MySQL | 9.x |
| Server | Uvicorn | 0.39.0 |
| Email Validation | pydantic[email] | — |

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
- **Response wrapper** — uniform `{ success, data, message }` shape across all endpoints
- **bcrypt 4.0.1 pinned** — required for Python 3.9 compatibility with passlib

---

## 📁 Folder Structure

```
backend/
├── .env                     # Environment variables (never commit)
├── requirements.txt         # Python dependencies
└── app/
    ├── main.py              # Entry point — CORS config, router registration, table creation
    ├── config.py            # Pydantic settings loaded from .env
    ├── database.py          # SQLAlchemy engine, session factory, Base, get_db dependency
    │
    ├── models/              # ORM table definitions
    │   ├── __init__.py      # Exports all models
    │   └── user.py          # User model
    │
    ├── schemas/             # Pydantic request/response schemas
    │   └── user.py          # RegisterRequest, LoginRequest, UserResponse, AuthResponse
    │
    ├── routers/             # Route handlers (thin — delegate to services)
    │   └── auth.py          # /register, /login, /logout, /me
    │
    ├── services/            # Business logic (to be built per feature)
    │
    └── utils/
        └── auth.py          # hash_password, verify_password, create_access_token,
                             # decode_access_token, get_current_user
```

---

## ⚙️ Getting Started

### Prerequisites

- Python `3.9+`
- MySQL `8+` or `9+` running locally
- A database named `lifeos` already created

### Create the database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE IF NOT EXISTS lifeos;
EXIT;
```

### Installation

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

API base: [http://localhost:8000](http://localhost:8000)
Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)

> Tables are auto-created on startup via `Base.metadata.create_all()`

---

## 🔑 Environment Variables

Create a `.env` file in `backend/`:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/lifeos
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRONTEND_URL=http://localhost:3000
```

---

## 🗃️ Database Schema

```sql
CREATE TABLE users (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  email      VARCHAR(150) UNIQUE NOT NULL,
  password   VARCHAR(255) NOT NULL,        -- bcrypt hashed
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Coming in Phase 3+
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

---

## 🔌 API Reference

Base URL: `/api/v1`

### Auth ✅ (Implemented)
| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `POST` | `/auth/register` | No | Create account, sets httpOnly cookie |
| `POST` | `/auth/login` | No | Login, sets httpOnly cookie |
| `POST` | `/auth/logout` | No | Clears auth cookie |
| `GET` | `/auth/me` | Yes | Get current user from cookie |

### Tasks — Planner (Coming Phase 3)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/tasks?date=YYYY-MM-DD` | Fetch tasks for a date |
| `POST` | `/tasks` | Create a task |
| `PATCH` | `/tasks/:id` | Update task |
| `DELETE` | `/tasks/:id` | Delete a task |

### DSA (Coming Phase 4)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dsa/logs?from=&to=` | Fetch logs in date range |
| `POST` | `/dsa/logs` | Log a solved problem |
| `GET` | `/dsa/stats` | Aggregated stats |
| `DELETE` | `/dsa/logs/:id` | Delete a log |

### Fitness (Coming Phase 5)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/fitness/logs?from=&to=` | Fetch logs |
| `POST` | `/fitness/logs` | Add daily log |
| `PATCH` | `/fitness/logs/:id` | Update log |
| `GET` | `/fitness/stats` | Aggregated stats |

### Streaks (Coming Phase 5)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/streaks/me` | Get current and best streak |
| `POST` | `/streaks/checkin` | Record today's activity |

---

## 🔐 Authentication Flow

```
POST /auth/register or /auth/login
         │
         ▼
  Validate request (Pydantic)
         │
         ▼
  Hash password (bcrypt) / Verify password
         │
         ▼
  Create JWT: { sub: user_id, exp: now + 1440min }
         │
         ▼
  Set httpOnly cookie: access_token=<jwt>
         │
         ▼
  Return { success, message, user } — password never in response
```

**Protected route flow:**
```
Request with cookie
         │
         ▼
  get_current_user dependency
         │
         ▼
  Decode JWT from cookie
         │
         ▼
  Query DB for user
         │
         ▼
  Inject user into route handler
```

---

## 📦 Dependencies

```
fastapi==0.128.8
uvicorn==0.39.0
sqlalchemy==2.x
pymysql==1.x
python-jose[cryptography]==3.5.0
passlib==1.7.4
bcrypt==4.0.1          # Pinned — required for Python 3.9 compatibility
pydantic==2.x
pydantic-settings==2.x
pydantic[email]        # Required for EmailStr validation
python-dotenv
```

---

## 🗺️ Roadmap

- [x] Phase 1 — Project setup, venv, folder structure
- [x] Phase 2 — Auth (register, login, logout, /me) with JWT httpOnly cookies
- [ ] Phase 3 — Planner API (tasks CRUD)
- [ ] Phase 4 — DSA API (logs + stats)
- [ ] Phase 5 — Fitness + Streaks API
- [ ] Phase 6 — Alembic migrations setup
- [ ] Phase 7 — Deployment (Railway / Render)

---

## 🧠 Engineering Principles

- **Thin routers** — route handlers only parse requests and return responses
- **Fail fast** — Pydantic v2 validates at the boundary; bad data never reaches the DB
- **Secure by default** — httpOnly cookies, bcrypt, password never returned in responses
- **Auto table creation** — `Base.metadata.create_all()` on startup for dev convenience

---

## 🔗 Related

- [LifeOS Frontend](https://github.com/sahilkriplani/lifeos-frontend) — Next.js 16 + React 19

---

## 👤 Author

**Sahil Kriplani** — Full-Stack Developer, Ahmedabad 🇮🇳
GitHub: [@sahilkriplani](https://github.com/sahilkriplani)

> *"Clean APIs. Scalable systems. Production mindset."*