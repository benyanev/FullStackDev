# SocialApp

A full-stack social media application built with **React + Material UI** on the frontend and **Flask + MySQL** on the backend. Features secure user authentication with server-side UUID sessions, HttpOnly cookies, bcrypt password hashing, a WYSIWYG rich text editor, image uploads, follow/unfollow system, and infinite scroll.

## Features

- **Authentication** — Signup and Login with bcrypt password hashing and server-side UUID sessions. Sessions are transported via HttpOnly cookies and persist across page refreshes securely (no localStorage). Rate-limited auth endpoints prevent brute-force attacks.
- **Feed** — Infinite-scrolling post grid with two tabs:
  - **Global Feed** — all posts from all users.
  - **Following Feed** — posts only from users you follow (requires login).
- **Rich Text Posts** — Create posts with a **Tiptap** WYSIWYG editor (bold, italic, strikethrough, lists, code, blockquote) and optionally attach images. Post bodies are stored as HTML and rendered safely with **DOMPurify** sanitization.
- **Image Uploads** — Attach images to posts and upload profile pictures. Files are validated (type + size) and stored on the server.
- **User Profiles** — Dedicated profile page for each user showing name, bio, profile picture, follower/following counts (with detail dialogs), and their posts. Users can edit their own profile.
- **Follow System** — Follow/unfollow other users from their profile page or user cards. Follower and following counts update in real time.
- **User Search** — Autocomplete search bar that filters users by name in real time.
- **Timestamps** — All posts show human-readable "time ago" labels (e.g., "2 hours ago", "3 days ago").
- **Expandable Posts** — Post cards clamp the body to 3 visible lines; a "Read More" button appears when content overflows.
- **Infinite Scroll** — Posts and user lists auto-load as you scroll down using IntersectionObserver.

## Routes

| Path | Component | Auth? | Description |
|---|---|---|---|
| `/` | Feed | No | Global feed — all posts, infinite scroll |
| `/users` | Users | No | User directory with search and infinite scroll |
| `/profile/:userId` | UserProfile | No | User profile with bio, avatar, followers, posts |
| `/user-posts/:userId` | Feed | No | Posts by a specific user |
| `/login` | Login | No | Login form |
| `/signup` | Signup | No | Registration form |
| `/new-post` | NewPost | Yes | Create a new post (Tiptap editor + image upload) |

## API Endpoints

| Method | Endpoint | Auth? | Description |
|---|---|---|---|
| `POST` | `/api/signup` | No | Register a new user; sets session cookie |
| `POST` | `/api/login` | No | Authenticate a user; sets session cookie |
| `POST` | `/api/logout` | No | Destroy session and clear cookie |
| `GET` | `/api/me` | Yes | Get current user from session cookie |
| `GET` | `/api/posts?_start=0&_limit=10&userId=` | No | Paginated posts (optional user filter) |
| `GET` | `/api/posts/following?_start=0&_limit=10` | Yes | Posts from followed users |
| `POST` | `/api/posts` | Yes | Create a new post (title, body HTML, optional image_url) |
| `POST` | `/api/upload/image` | Yes | Upload a post image |
| `GET` | `/api/users?_start=0&_limit=100` | No | Paginated users |
| `GET` | `/api/users/:id` | No | Single user by ID |
| `PUT` | `/api/users/:id/profile` | Yes | Update name, bio, and profile picture |
| `POST` | `/api/upload/profile-picture` | Yes | Upload a profile picture |
| `POST` | `/api/users/:id/follow` | Yes | Follow a user |
| `DELETE` | `/api/users/:id/follow` | Yes | Unfollow a user |
| `GET` | `/api/users/:id/followers` | No | Get user's followers list |
| `GET` | `/api/users/:id/following` | No | Get users they follow |
| `GET` | `/api/users/:id/is-following` | Yes | Check if current user follows target |

## Tech Stack

### Frontend
- **React 19** — UI library
- **React Router 7** — Client-side routing
- **Vite 8** — Build tool and dev server
- **Material UI (MUI) v9** — Component library
- **Tiptap** — WYSIWYG rich text editor (StarterKit)
- **DOMPurify** — HTML sanitization for XSS prevention

### Backend
- **Flask 3** — Python micro-framework (REST API)
- **MySQL** — Relational database
- **bcrypt** — Password hashing
- **UUID sessions** — Server-side session management with HttpOnly cookies
- **Flask-CORS** — Cross-Origin Resource Sharing
- **Flask-Limiter** — Rate limiting on auth endpoints

## Database Schema

See [database_schema.md](database_schema.md) for the full ER diagram and table documentation.

**Tables:** `users`, `posts`, `sessions`, `follows`

## Project Structure

```
myReact/
├── .env                        # Database credentials
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── PROJECT_STATUS.md           # Development progress tracker
├── database_schema.md          # Database ER diagram (Mermaid)
├── backend/
│   ├── init_db.sql             # SQL schema (users, posts, sessions, follows)
│   ├── migrate_v2.sql          # Migration: follows table
│   ├── migrate_v3.sql          # Migration: bio + profile_picture on users
│   ├── migrate_v4.sql          # Migration: image_url on posts
│   ├── db.py                   # Database CRUD helpers
│   ├── app.py                  # Flask REST API (17 endpoints)
│   └── static/uploads/         # Uploaded files (profiles/, posts/)
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
            ├── TopBar.jsx      # Sticky nav bar (auth-aware, profile link)
            ├── Feed.jsx        # Infinite-scrolling post grid (Global/Following tabs)
            ├── SinglePost.jsx  # Expandable post card (rich HTML + images)
            ├── Users.jsx       # Infinite-scrolling user directory
            ├── User.jsx        # User info card (follow/unfollow)
            ├── UserProfile.jsx # Full user profile page (bio, avatar, followers)
            ├── Search.jsx      # Autocomplete search by name
            ├── Login.jsx       # Login form
            ├── Signup.jsx      # Registration form
            └── NewPost.jsx     # Post creation (Tiptap editor + image upload)
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
2. **Create Post** — publish a post with rich text formatting and an image
3. **Feed** — posts display with author info, timestamps, and images
4. **Following Feed** — follow a user, switch to the "Following" tab
5. **Profile** — click a username to view their profile, edit your own profile
6. **Search** — search for users by name in the Users page
7. **Infinite Scroll** — scroll down to auto-load more posts/users
8. **Refresh** — session persists (cookie-based, no localStorage)
9. **Logout / Login** — session is destroyed and restored correctly
