
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
