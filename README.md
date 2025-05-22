
# 🗓️ Collaborative Event Management System

A robust, secure, and scalable **event management backend** built using **FastAPI** and **PostgreSQL**, featuring user authentication, role-based access control, event versioning, and changelog tracking.

---

## 🚀 Features

- ✅ User Registration & Login (JWT-based)
- 🔐 Secure password hashing (via `bcrypt`)
- 📆 Event creation with optional recurrence
- 👥 Role-based access to events
- 🛠️ Full CRUD operations for Events and Users
- 📚 Event Versioning and Changelog tracking
- 📎 Permission system (user-role-event relationships)
- 📦 Modular and extensible architecture

---

## 🏗️ Tech Stack

| Component      | Technology     |
|----------------|----------------|
| Backend        | FastAPI        |
| Database       | PostgreSQL     |
| ORM            | SQLAlchemy     |
| Auth           | JWT + OAuth2   |
| Schema Models  | Pydantic       |

---

## 📁 Project Structure

```
Assignment/
├── app/
│   ├── api/             # Routers and dependencies
│   ├── core/            # Config and security
│   ├── crud/            # Database operations
│   ├── db/              # DB session setup
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── main.py          # Entry point
├── requirements.txt
└── .env                 # Environment variables
```

---

## 🧪 Setup & Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root folder with the following content:

```env
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/your_database
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Run the Application
```bash
uvicorn app.main:app --reload
```

App will be available at: `http://127.0.0.1:8000`

---

## 🧬 Database Schema

Includes the following tables:
- `users`: User accounts
- `roles`: Role definitions
- `events`: Core event data
- `event_permissions`: Link table for user-role-event
- `event_versions`: Snapshots of events
- `changelog`: Tracks what changed and by whom

SQL setup included in `docs/schema.sql` or see the schema section in project documentation.

---

## 🔐 API Endpoints

Interactive API Docs available at:

- Swagger UI: [`/docs`](http://localhost:8000/docs)
- Redoc: [`/redoc`](http://localhost:8000/redoc)

---

## 📌 TODO / Future Scope

- [ ] Web frontend integration
- [ ] Notification system (email/SMS)
- [ ] Recurrence rule parser
- [ ] Admin dashboard
- [ ] Dockerize the app

---

## 🤝 Contributing

1. Fork this repo
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**  
[GitHub](https://github.com/YOUR_USERNAME) • [LinkedIn](https://linkedin.com/in/YOUR_LINK)

---

---

## 🧾 PostgreSQL Table Schemas

Below are the SQL definitions for all tables used in this project:

```sql
-- Table for Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Table for Roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);

-- Table for Events
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    location VARCHAR(255),
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_recurring BOOLEAN DEFAULT FALSE NOT NULL,
    recurrence_pattern JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Table for Event Permissions
CREATE TABLE event_permissions (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    UNIQUE (event_id, user_id)
);

-- Table for Event Versions
CREATE TABLE event_versions (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    data JSONB NOT NULL,
    changed_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE (event_id, version_number)
);

-- Table for Changelog
CREATE TABLE changelog (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    version_id INTEGER REFERENCES event_versions(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    changes JSONB NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);

CREATE INDEX IF NOT EXISTS idx_events_owner_id ON events(owner_id);
CREATE INDEX IF NOT EXISTS idx_events_start_time ON events(start_time);

CREATE INDEX IF NOT EXISTS idx_event_permissions_event_id ON event_permissions(event_id);
CREATE INDEX IF NOT EXISTS idx_event_permissions_user_id ON event_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_event_permissions_role_id ON event_permissions(role_id);

CREATE INDEX IF NOT EXISTS idx_event_versions_event_id ON event_versions(event_id);
CREATE INDEX IF NOT EXISTS idx_event_versions_changed_by_user_id ON event_versions(changed_by_user_id);

CREATE INDEX IF NOT EXISTS idx_changelog_event_id ON changelog(event_id);
CREATE INDEX IF NOT EXISTS idx_changelog_version_id ON changelog(version_id);
CREATE INDEX IF NOT EXISTS idx_changelog_user_id ON changelog(user_id);
CREATE INDEX IF NOT EXISTS idx_changelog_timestamp ON changelog(timestamp);
```

---

## 🗄️ PostgreSQL Table Schemas & Relationships

### 🔹 `users`
Stores basic user information.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

---

### 🔹 `roles`
Defines different roles that users can have in events.

```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);
```

---

### 🔹 `events`
Stores events created by users, including optional recurrence.

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    location VARCHAR(255),
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_recurring BOOLEAN DEFAULT FALSE NOT NULL,
    recurrence_pattern JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

---

### 🔹 `event_permissions`
Links users to events with specific roles (one role per user per event).

```sql
CREATE TABLE event_permissions (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    UNIQUE (event_id, user_id)
);
```

---

### 🔹 `event_versions`
Stores snapshots of event data to track historical versions.

```sql
CREATE TABLE event_versions (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    data JSONB NOT NULL,
    changed_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE (event_id, version_number)
);
```

---

### 🔹 `changelog`
Tracks specific changes made to events (field-level granularity).

```sql
CREATE TABLE changelog (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    version_id INTEGER REFERENCES event_versions(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    changes JSONB NOT NULL
);
```

---

## 🔗 Entity Relationships

- `users` ↔ `events` → One-to-Many (`owner_id`)
- `users` ↔ `event_permissions` → Many-to-Many via `event_permissions`
- `roles` ↔ `event_permissions` → One-to-Many
- `events` ↔ `event_versions` → One-to-Many
- `event_versions` ↔ `changelog` → One-to-One or Many-to-One
- `users` ↔ `event_versions`/`changelog` → Optional reference to track changes made

---
