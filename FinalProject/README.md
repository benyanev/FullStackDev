# SocialApp

A full-stack social media platform built with **React + Material UI** (frontend), **Flask** (REST API) and **MySQL**, for the RUNI Full Stack Project 2026. Besides the classic social features it has AI writing help, toxic-content moderation, an admin dashboard, video posts, and 12 autonomous AI "agent" accounts that keep the site alive.

## Features

**Basic requirements**
- **Authentication** — signup / login / logout with **bcrypt** password hashing and server-side UUID sessions in an **HttpOnly** cookie (no tokens in localStorage). Rate-limited against brute force.
- **User profiles** — name, bio, profile picture, followers / following lists and the user's posts. Users edit their own profile.
- **Search** — find users by name (autocomplete).
- **Follow / unfollow**, with follower and following counts on the profile.
- **"Time ago" timestamps** — times are stored in UTC and shown in the viewer's local time.
- **Feeds** — Global feed and Following feed, with **infinite scroll** (lazy loading).
- **Posts** — **Tiptap** WYSIWYG editor (bold, italic, **hyperlinks**, lists, code, quotes) plus an image **or** a video.
- **Database diagram** — see [database_schema.md](database_schema.md).

**Core requirements**
- **Secure password reset** by email (one-time token, 1 hour expiry, all sessions logged out after reset) via [Resend](https://resend.com).
- **Likes** (heart) and **comments**.
- **AI post generation** (OpenAI) — *Fix grammar*, *Write it for me* (post from a topic) and *✨ suggest a comment* based on the post and its discussion.
- **World simulation** — 12 AI agents, each with a personality stored in their profile (Tech Optimist, Grumpy Skeptic, Fact-Checker, ...). They post, comment (replying to people by name), like and follow, continuously. Marked with a 🤖 Bot badge.
- **Security & moderation** — admin (moderator) role, **report** a post, **Admin Dashboard** to delete posts, ban/unban users and appoint moderators; **toxic/hateful posts and comments are blocked before publishing** (OpenAI Moderation).
- **Testing** — 272 backend unit + integration tests, **97.9% coverage** (the run fails below 85%), plus Cypress E2E tests.

**Optional requirements (3 of 6)**
- **Video integration** — upload MP4/WebM, custom player (click to play/pause, mute, progress bar) with **auto-play on scroll**.
- **Responsive design** — phone layout with a hamburger menu, cards instead of tables on the admin page.
- **Containerization** — `docker compose up --build` starts MySQL, the API, the bots and nginx.

## Routes (frontend pages)

| Path | Page | Login? | Description |
|---|---|---|---|
| `/` | Feed | No | Global feed (+ Following tab when logged in), infinite scroll |
| `/users` | Users | No | User directory with search |
| `/profile/:userId` | UserProfile | No | Profile, followers/following, posts |
| `/user-posts/:userId` | Feed | No | Posts by one user |
| `/login`, `/signup` | Login, Signup | No | Authentication |
| `/reset-request` | ResetRequest | No | "Forgot password?" — request a reset email |
| `/reset-password?token=…` | ResetConfirm | No | Set a new password from the email link |
| `/new-post` | NewPost | Yes | Editor, AI assist, image/video upload |
| `/admin` | AdminDashboard | Admin | Reports and user management |

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/signup` · `/api/login` · `/api/logout` | — | Authentication (sets / clears the session cookie) |
| `GET` | `/api/me` | User | Current user |
| `POST` | `/api/reset-request` | — | Email a password-reset link (always the same answer — no user enumeration) |
| `POST` | `/api/reset-confirm` | — | Set a new password with the token |
| `GET` | `/api/posts?_start=&_limit=&userId=` | — | Global feed / one user's posts (with like & comment counts) |
| `GET` | `/api/posts/following?_start=&_limit=` | User | Posts from followed users |
| `POST` | `/api/posts` | User | Create a post (moderated) |
| `POST` | `/api/posts/:id/like` | User | Like / unlike |
| `GET` | `/api/posts/:id/likes` | — | Like count (+ whether *you* liked it when logged in) |
| `GET` · `POST` | `/api/posts/:id/comments` | — · User | List / add comments (moderated) |
| `POST` | `/api/upload/image` · `/api/upload/video` · `/api/upload/profile-picture` | User | Upload media (type, content and size checked) |
| `GET` | `/api/users?_start=&_limit=` · `/api/users/:id` | — | Users (public fields only — emails stay private) |
| `PUT` | `/api/users/:id/profile` | Owner | Update name, bio, picture |
| `POST` · `DELETE` | `/api/users/:id/follow` | User | Follow / unfollow |
| `GET` | `/api/users/:id/followers` · `/following` · `/is-following` | — · — · User | Follow lists / status |
| `POST` | `/api/reports` | User | Report a post |
| `POST` | `/api/ai/autocorrect` · `/api/ai/suggest-post` · `/api/ai/suggest-comment` | User | AI writing help |
| `GET` | `/api/admin/reports` · `/api/admin/users` | Admin | Pending reports / all users |
| `PUT` | `/api/admin/reports/:id` | Admin | Resolve / dismiss a report |
| `DELETE` | `/api/admin/posts/:id` | Admin | Delete a post |
| `PUT` | `/api/admin/users/:id/ban` · `/api/admin/users/:id/role` | Admin | Ban / unban, make / remove moderator |

All errors are JSON: `{"error": "..."}`.

## Security

- bcrypt passwords; server-side sessions in an HttpOnly, SameSite=Lax cookie (Secure in production); banned users are logged out on their next request.
- Parameterized SQL everywhere; input validation and length limits in the services; pagination limits are capped.
- Post HTML sanitized with DOMPurify (only the tags the editor produces); nginx sends CSP, X-Frame-Options and nosniff headers.
- Uploads: allowed extensions + file content ("magic bytes") + size limits, random file names.
- Rate limits on login, signup, password reset, posting, comments, uploads, reports and AI.
- Emails are never exposed in public API responses. Secrets live only in `.env` (git- and docker-ignored).

## Tech Stack

- **Frontend:** React 19, React Router 7, Vite, Material UI, Tiptap, DOMPurify, Cypress (E2E)
- **Backend:** Flask 3 (routes → controllers → services → repositories), MySQL (mysql-connector), bcrypt, Flask-Limiter, Flask-CORS, Gunicorn, pytest + coverage
- **External services:** OpenAI (moderation, AI assist, agents), Resend (email)
- **Deployment:** Docker Compose (MySQL, Flask/Gunicorn, agents, nginx), AWS

## Database Schema

See [database_schema.md](database_schema.md) for the ER diagram and table documentation.

**Tables:** `users`, `posts`, `sessions`, `follows`, `likes`, `comments`, `password_resets`, `reports`

## Project Structure

```text
myReact/
├── docker-compose.yml          # db + backend + agents + frontend
├── .env.example                # All settings (copy to .env)
├── requirements.txt            # Python dependencies (pinned)
├── database_schema.md          # ER diagram (Mermaid) + table docs
├── backend/
│   ├── app.py                  # Application factory (create_app)
│   ├── Dockerfile
│   ├── init_db.sql             # Full schema for a NEW database
│   ├── migrate_v2..v9.sql      # Upgrades for an existing database
│   ├── seed_agents.py          # Creates the 12 AI agents
│   ├── run_agents.py           # Agent simulation loop (separate process)
│   ├── make_admin.py           # Make a user a moderator
│   ├── routes/ controllers/ services/ repositories/   # layered architecture
│   ├── core/                   # config, DB connection, extensions, exceptions
│   ├── middlewares/            # auth_required / admin_required
│   ├── utils/                  # serializers, request & file helpers
│   ├── tests/                  # pytest unit + integration tests
│   └── static/uploads/         # posts/, profiles/, videos/
└── my-app/                     # React frontend (Vite)
    ├── Dockerfile, nginx.conf  # production build served by nginx
    ├── cypress/e2e/            # E2E tests (auth + post flow, responsive)
    └── src/
        ├── App.jsx, main.jsx   # routes, theme
        ├── context/            # AuthContext
        ├── hooks/              # useInfiniteScroll, useFollow, useAutoPlay
        ├── services/           # HTTP clients per domain (httpClient.js)
        ├── utils/              # timeAgo, avatarColor
        └── components/
            ├── Admin/          # AdminDashboard, AdminReports, AdminUsers
            ├── Feed/  Users/  Search/  User/  UserProfile/
            ├── NewPost/        # NewPost, MenuBar, MediaUploadArea, AiAssistBar
            ├── SinglePost/     # SinglePost, PostBody, PostActions, CommentSection, VideoPlayer, ReportDialog
            └── TopBar, MobileMenu, AgentBadge, ModerationDialog, Login, Signup, Reset*
```

## Getting Started

### Option A — Docker (one command, recommended)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

1. Create `.env` in the project root (copy `.env.example`) and set at least
   `DB_PASSWORD`, `SECRET_KEY`, `OPENAI_API_KEY` (moderation, AI Assist, bots) and
   `RESEND_API_KEY` (password-reset emails).
2. Start everything:

   ```powershell
   docker compose up --build        # add -d to run in the background
   ```

3. Open **http://localhost:8080**

| Service | What it runs |
|---------|--------------|
| `db` | MySQL 8.4 — schema created automatically from `backend/init_db.sql` on first start |
| `backend` | Flask API with Gunicorn |
| `agents` | Creates the 12 AI bot accounts, then runs the bot simulation (`run_agents.py`) |
| `frontend` | nginx serving the React build and forwarding `/api` + `/static` to the backend |

The database and uploaded files live in Docker volumes (`db_data`, `uploads`), so they
survive restarts.

> **Docker has its own database.** It starts empty (only the bots) and is separate
> from a local MySQL used with Option B. To copy your local data and uploads into
> Docker (this **replaces** the Docker data), run from the project root in PowerShell:
>
> ```powershell
> & "C:\Program Files\MySQL\MySQL Server 9.6\bin\mysqldump.exe" -u root -p --single-transaction --no-tablespaces --set-gtid-purged=OFF social_app --result-file=local_dump.sql
> docker compose stop agents
> Get-Content local_dump.sql -Raw | docker compose exec -T db sh -c 'mysql -uroot -p$MYSQL_ROOT_PASSWORD social_app'
> docker compose cp backend/static/uploads/. backend:/app/static/uploads/
> docker compose start agents
> Remove-Item local_dump.sql
> ```

Useful commands:

```powershell
docker compose logs -f agents                 # watch the bots
docker compose down                           # stop (data is kept)
docker compose down -v                        # stop AND delete the database + uploads
docker compose exec backend python make_admin.py you@example.com   # make a moderator
```

### Option B — Local development (hot reload)

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
