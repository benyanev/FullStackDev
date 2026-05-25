# SocialApp

A full-stack social media application built with **React + Material UI** on the frontend and **Flask + MySQL** on the backend. Features secure user authentication with server-side UUID sessions, HttpOnly cookies, and bcrypt password hashing.

## Features

- **Authentication** — Signup and Login with bcrypt password hashing and server-side UUID sessions. Sessions are transported via HttpOnly cookies and persist across page refreshes securely (no localStorage).
- **Feed** — Paginated post grid (10 at a time) with "Load More". Supports a global feed (`/`) and per-user feed (`/user-posts/:userId`).
- **Expandable Posts** — Post cards clamp the body to 3 visible lines; a "Read More" button appears when content overflows.
- **Users Directory** — Paginated user list with an autocomplete search bar that filters by email in real time.
- **New Post** — Authenticated users can publish posts with a title and body, saved to the MySQL database.

## Routes

| Path | Component | Auth? | Description |
|---|---|---|---|
| `/` | Feed | No | Global feed — all posts, paginated |
| `/users` | Users | No | User directory with search and pagination |
| `/user-posts/:userId` | Feed | No | Posts by a specific user |
| `/login` | Login | No | Login form |
| `/signup` | Signup | No | Registration form |
| `/new-post` | NewPost | Yes | Create a new post |

## API Endpoints

| Method | Endpoint | Auth? | Description |
|---|---|---|---|
| `POST` | `/api/signup` | No | Register a new user; sets session cookie |
| `POST` | `/api/login` | No | Authenticate a user; sets session cookie |
| `POST` | `/api/logout` | No | Destroy session and clear cookie |
| `GET` | `/api/me` | Yes | Get current user from session cookie |
| `GET` | `/api/posts?_start=0&_limit=10&userId=` | No | Paginated posts (optional user filter) |
| `POST` | `/api/posts` | Yes | Create a new post |
| `GET` | `/api/users?_start=0&_limit=100` | No | Paginated users |
| `GET` | `/api/users/:id` | No | Single user by ID |

## Tech Stack

### Frontend
- **React 19** — UI library
- **React Router 7** — Client-side routing
- **Vite 8** — Build tool and dev server
- **Material UI (MUI) v9** — Component library

### Backend
- **Flask 3** — Python micro-framework (REST API)
- **MySQL** — Relational database
- **bcrypt** — Password hashing
- **UUID sessions** — Server-side session management with HttpOnly cookies
- **Flask-CORS** — Cross-Origin Resource Sharing

## Project Structure

```
myReact/
├── .env                        # Database credentials
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── backend/
│   ├── init_db.sql             # SQL schema (users, posts, sessions tables)
│   ├── db.py                   # Database CRUD helpers (users, posts, sessions)
│   └── app.py                  # Flask REST API (8 endpoints)
└── my-app/                     # React frontend (Vite)
    ├── package.json
    └── src/
        ├── main.jsx            # React entry point
        ├── App.jsx             # Root component — Router + AuthProvider
        ├── index.css           # Global styles
        ├── context/
        │   └── AuthContext.jsx # Auth state (cookie-based sessions)
        ├── services/
        │   └── api.js          # Fetch wrappers for all backend endpoints
        └── components/
            ├── TopBar.jsx      # Sticky nav bar (auth-aware)
            ├── Feed.jsx        # Paginated post grid
            ├── SinglePost.jsx  # Expandable post card
            ├── Users.jsx       # User directory page
            ├── User.jsx        # User info card
            ├── Search.jsx      # Autocomplete search by email
            ├── Login.jsx       # Login form
            ├── Signup.jsx      # Registration form
            └── NewPost.jsx     # Post creation form (auth required)
```

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) v18+
- [Python](https://python.org/) 3.10+
- [MySQL](https://mysql.com/) server running locally

### 1. Initialize the Database

Run the SQL init script to create the `social_app` database and tables:

```powershell
# PowerShell — pipe the SQL file into the MySQL CLI
Get-Content backend\init_db.sql -Raw | & "C:\Program Files\MySQL\MySQL Server 9.6\bin\mysql.exe" -u root -p
```

> **Note:** Adjust the MySQL path if your version differs. The command will prompt for your MySQL root password.

### 2. Start the Backend

```powershell
cd myReact
python -m venv .venv          # Create virtual environment (first time only)
.\.venv\Scripts\Activate      # Activate virtual environment
pip install -r requirements.txt
python backend\app.py         # Starts Flask on http://localhost:5000
```

Leave this terminal open.

### 3. Start the Frontend

Open a **second terminal**:

```powershell
cd myReact\my-app
npm install                   # Install dependencies (first time only)
npm run dev                   # Starts Vite on http://localhost:5173
```

### 4. Test the App

Open **http://localhost:5173** and verify:

1. **Signup** — register a new account
2. **Create Post** — publish a post (appears in the feed)
3. **Feed** — posts display with author info and expandable body
4. **Refresh** — session persists (cookie-based, no localStorage)
5. **Logout / Login** — session is destroyed and restored correctly
6. **Users** — user directory loads with search functionality
