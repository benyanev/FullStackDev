# SocialApp — Project Status & Agent Handoff Document

> **Last updated**: 2026-09-23  
> **Purpose**: This document gives any AI agent (or developer) full context to continue building this project from exactly where we left off.

---

## 1. Project Overview

**What**: A TikTok-style social media platform built as an academic final project.  
**Stack**: Flask (Python) backend + React 19 / Vite / MUI frontend + MySQL database.  
**Workspace root**: `c:\Users\benya\CS\FullStackDev\myReact`  
**Requirements PDF**: `RUNI Full Stack Project 2026 (1).pdf` (in workspace root)

---

## 2. Architecture

```
BROWSER (React 19 / Vite / MUI)
  Components → Hooks → Services (httpClient.js) → /api/*
                          │ HTTP (JSON + HttpOnly Cookies)
FLASK MONOLITH
  Routes (Blueprints) → Controllers → Services → Repos → MySQL
  Middleware: auth_required (session cookie validation)
  Extensions: CORS, Flask-Limiter
  Sessions: Server-side in MySQL (HttpOnly cookie)
                          │
                  MySQL 9.6 (DB: social_app)
```

### Backend Structure (`backend/`)

```
backend/
├── app.py                    # Application factory (create_app)
├── core/
│   ├── config.py             # ENV vars, SECRET_KEY, DB creds, UPLOAD_FOLDER
│   ├── database.py           # get_connection() → mysql-connector-python
│   ├── exceptions.py         # AppError, ValidationError(400), NotFoundError(404), AuthError(401)
│   └── extensions.py         # CORS, Flask-Limiter instances
├── middlewares/
│   └── auth_middleware.py    # @auth_required decorator (checks session cookie)
├── repositories/             # Raw SQL, each function opens/closes its own connection
│   ├── user_repository.py    # get_user_by_id, get_user_by_email, create_user, update_profile, update_password_hash
│   ├── post_repository.py    # get_post_by_id, get_posts_paginated, create_post
│   ├── session_repository.py # create_session, get_session, delete_session, delete_expired_sessions
│   ├── follow_repository.py  # add_follow, remove_follow, get_followers, get_following, is_following
│   ├── like_repository.py    # add_like, remove_like, get_like_count, has_user_liked
│   ├── comment_repository.py # create_comment, get_comments_by_post, get_comment_count
│   └── reset_repository.py   # create_reset_token, get_reset_by_token, mark_token_used, invalidate_user_tokens
├── services/                 # Business logic, raises AppError subclasses
│   ├── auth_service.py       # signup, login, logout, get_current_user
│   ├── follow_service.py     # toggle_follow, get_followers, get_following
│   ├── like_service.py       # toggle_like, get_post_likes
│   ├── comment_service.py    # add_comment, get_comments
│   ├── reset_service.py      # request_reset, confirm_reset
│   ├── email_service.py      # send_email (dev: prints to console; prod: Gmail SMTP)
│   ├── post_service.py       # create_post
│   ├── upload_service.py     # save_image, save_profile_picture
│   └── user_service.py       # get_users, update_profile
├── controllers/              # Parse HTTP request → call service → return JSON
├── routes/                   # Flask Blueprints, URL mapping + middleware decorators
├── utils/
│   └── serializers.py        # serialize_dates_list (datetime → ISO string for JSON)
├── tests/                    # 272 tests total, all passing, 97.9% coverage
└── static/uploads/           # User-uploaded files (posts/ + profile_pictures/)
```

### Frontend Structure (`my-app/src/`)

```
my-app/src/
├── App.jsx                   # Root: BrowserRouter + AuthProvider + Routes
├── context/AuthContext.jsx   # user, loading, login(), signup(), logout()
├── services/                 # httpClient.js + domain services (auth, posts, likes, comments, reset, etc.)
├── hooks/                    # useInfiniteScroll.js, useFollow.js
├── components/
│   ├── TopBar.jsx, Login.jsx, Signup.jsx
│   ├── ResetRequest.jsx, ResetConfirm.jsx
│   ├── Feed/ (Feed.jsx, useFeed.js)
│   ├── SinglePost/ (SinglePost.jsx, PostHeader.jsx, PostBody.jsx, PostActions.jsx, CommentSection.jsx)
│   ├── NewPost/ (Tiptap rich text editor)
│   ├── Users/, UserProfile/, Search/
└── utils/ (avatarColor.js, timeAgo.js)
```

---

## 3. Database

**Tables**: `users`, `posts`, `sessions`, `follows`, `likes`, `comments`, `password_resets`, `reports`  
**Full schema**: `database_schema.md` (workspace root)  
**Migrations applied**: `migrate_v1.sql` through `migrate_v6.sql` (v7 = Phase 3, v8 = Phase 6, v9 = Phase 8 — run manually)  
**Credentials**: Host=`localhost`, User=`root`, DB=`social_app` — password lives in `.env` only (never commit it)

---

## 4. Completed Phases

### Phase 1: Likes & Comments (Core 2b) ✅
- `likes` + `comments` tables, full backend stack, PostActions.jsx + CommentSection.jsx
- 12 tests (6 unit + 6 integration)
- API: `POST/GET /api/posts/<id>/like`, `POST/GET /api/posts/<id>/comments`

### Phase 2: Password Reset (Core 2a) ✅
- `password_resets` table, email_service (Resend HTTP API via `RESEND_API_KEY` in `.env`; dev: console print), reset_service (token gen + validation)
- Send errors return 503; email/FRONTEND_URL config in `core/config.py`. Test sender onboarding@resend.dev only delivers to the Resend account owner
- ResetRequest.jsx + ResetConfirm.jsx + "Forgot password?" on Login
- 14 tests (9 unit + 5 integration)
- API: `POST /api/reset-request`, `POST /api/reset-confirm`

### Phase 3: Admin & Moderation (Core 2e i–ii) ✅
- `migrate_v7.sql`: `users.role` ENUM('user','admin'), `users.is_banned`, `reports` table (posts only, UNIQUE reporter+post, ON DELETE CASCADE)
- First admin: `UPDATE users SET role = 'admin' WHERE email = '...';`
- `admin_required` decorator (stacks on `auth_required`; 401 → 403). Banned users rejected at login (403); banning deletes their sessions
- report_repository, report_service (create), admin_service (reports, delete post, users, ban, role), report/admin controllers + routes
- Frontend: 🚩 flag button + ReportDialog in PostActions (hidden on own posts), `Admin/AdminDashboard.jsx` at `/admin` (Reports + Users tabs), "Admin" link in TopBar for admins
- 32 new tests (report/admin unit + integration, banned login)
- API: `POST /api/reports`, `GET /api/admin/reports`, `PUT /api/admin/reports/<id>`, `DELETE /api/admin/posts/<id>`, `GET /api/admin/users`, `PUT /api/admin/users/<id>/ban`, `PUT /api/admin/users/<id>/role`

### Phase 4: Sentiment Analysis (Core 2e.iii) ✅
- `services/sentiment_service.py`: `ensure_not_toxic(*texts)` → OpenAI Moderation API (`omni-moderation-latest`, stdlib urllib, no new dependency); strips HTML; raises `ModerationError` (422) if flagged
- Called in `comment_service.add_comment` and `post_service.create_post` (title + body in one call) BEFORE saving → toxic content is never stored
- Fails open (allowed + console warning) when `OPENAI_API_KEY` is missing or OpenAI is unreachable
- Frontend: httpClient errors now carry `.status`; `components/ModerationDialog.jsx` shown on 422 in CommentSection + NewPost (text kept for editing)
- `tests/conftest.py` autouse fixture blanks RESEND/OPENAI keys in every test (no accidental real API calls)
- 11 new tests (sentiment unit, post_service, comment toxic unit + integration)

### Phase 5: AI Post Generation (Core 2c) ✅
- `services/ai_service.py`: one `_chat()` helper → OpenAI Chat Completions (stdlib urllib), model from `OPENAI_MODEL` (default `gpt-4.1-mini`); errors → `AIUnavailableError` (503), real reason printed to console
- `autocorrect(text)` keeps Tiptap HTML tags; `suggest_post(topic)` → JSON `{title, body}` (simple HTML); `suggest_comment(post_id)` reads the post + last 10 comments from the DB (context comes from the server, not the client)
- API (login + 10/min rate limit): `POST /api/ai/autocorrect`, `/api/ai/suggest-post`, `/api/ai/suggest-comment`
- Frontend: `NewPost/AiAssistBar.jsx` ("Write it for me" topic dialog, "Fix grammar" for title + body), ✨ suggest button in CommentSection. AI output is still moderated when the user publishes.
- 20 new tests. NOTE: chat models need prepaid OpenAI credits (moderation is free).

### Phase 6: Agent Bots / World Simulation (Core 2d) ✅
- `migrate_v8.sql`: `users.is_agent`, `users.personality`; `seed_agents.py` creates 12 agents (idempotent, random unknown password, emails `*@agents.socialapp.local`)
- `services/agent_service.py`: `run_agent_tick()` → one random active (non-banned) agent does one weighted action: post 3 / comment 4 / like 2 / follow 1. Comments read the discussion and reply by @name; skips posts where the agent spoke last. Content goes through post/comment services → validation + toxicity check apply to bots too
- `ai_service.write_agent_post` / `write_agent_comment` (in-character prompts, avoids repeating recent titles)
- `run_agents.py`: separate process loop (`AGENT_INTERVAL_SECONDS`, default 60), `--once [action]` for testing. Not inside Flask (reloader/workers would duplicate actions) → own container later
- API responses now include `authorIsAgent` (posts, comments) and `is_agent`/`personality` (users). Frontend: `AgentBadge.jsx` "Bot" chip on posts, comments, profile (+ personality box), admin Users tab
- 12 new tests

### Phase 7: Testing to 85% (Core 2f) ✅ — 97.6% coverage
- `tests/test_repositories.py`: table-driven tests for every repository function with a MagicMock connection (return value, commit only on writes, cursor + connection always closed) + edge cases (optional filters, partial profile update, ban → 0/1)
- `tests/test_follow_user_services.py`, `tests/test_upload_service.py` (real FileStorage + tmp_path, nothing written to static/uploads), `tests/test_social_integration.py` (follows, users/profile, feeds, post creation, uploads via HTTP)
- `.coveragerc`: `fail_under = 85` → the test run FAILS if coverage drops below 85%; CLI scripts (seed_agents, run_agents, print_db) excluded
- Cypress spec fixed: types into Tiptap's contenteditable, finds the new post by text (bots may post first)
- Run: `python -m pytest tests/ --cov` → 221 passed, 97.63%

### Phase 8 (Optional 3d): Video Integration ✅
- `migrate_v9.sql`: `posts.video_url`. One attachment per post: image OR video (service rejects both)
- Backend: `upload_service.upload_video` (mp4/webm, 50 MB, `static/uploads/videos/`) sharing `_save_upload` with images; `POST /api/upload/video`; `MAX_CONTENT_LENGTH` + JSON 413 handler; post queries return `video_url`
- Frontend: `hooks/useAutoPlay.js` (IntersectionObserver, plays at ≥60% visible, pauses when out of view), `SinglePost/VideoPlayer.jsx` (custom UI: click play/pause, big ▶ overlay, mute toggle, progress bar, starts muted), `NewPost/MediaUploadArea.jsx` replaces ImageUploadArea (image or video + preview)
- 9 new tests (230 total, 97.7% coverage)

### Phase 9 (Optional 3b): Responsive Design ✅
- `main.jsx`: MUI ThemeProvider with `responsiveFontSizes(createTheme())` → headings shrink on phones
- `TopBar.jsx` + new `MobileMenu.jsx`: below `md` the button row is replaced by a hamburger → right Drawer (links, New Post, My Profile, Logout); "+ New Post" stays in the bar
- Page padding by breakpoint (`px: { xs: 2, sm: 3 }`, form cards `p: { xs: 2.5, sm: 4 }`) on all pages; ProfileCard smaller banner/avatar on phones, long emails wrap; Admin tables keep `minWidth: 600` and scroll sideways inside their container
- `cypress/e2e/responsive.cy.js`: 8 tests at 375×812 (no horizontal overflow on public pages + profile, hamburger works, desktop keeps the button row)

### Phase 10 (Optional 3f): Containerization — Docker ✅
- `docker compose up --build` → http://localhost:8080. Services: `db` (mysql:8.4, schema from `backend/init_db.sql`), `backend` (Gunicorn, 2 workers), `agents` (seed_agents + run_agents), `frontend` (node:24 build → nginx)
- `backend/init_db.sql` rewritten = full current schema (v1–v9) for NEW databases; migrations stay for upgrading existing ones
- `my-app/nginx.conf`: SPA fallback, proxies `/api` + `/static` to backend, `client_max_body_size 51m`
- Deploy-ready code: no hardcoded localhost in frontend (relative media URLs; Vite now also proxies `/static`), `CORS_ORIGINS` env, `BEHIND_PROXY=1` → ProxyFix (real client IP for rate limits), `FRONTEND_URL` from `PUBLIC_URL`
- Volumes `db_data`, `uploads` persist data. `.dockerignore` keeps `.env` out of images (secrets passed via `env_file`)
- `backend/make_admin.py <email>` (works in Docker and locally). `package-lock.json` regenerated (was out of sync → `npm ci` failed)
- Verified: all containers healthy, Cypress 10/10 against :8080, upload + restart persistence OK. 232 backend tests, 97.7%
- Fixes after user testing: nginx `resolver 127.0.0.11` + `set $backend` (nginx resolved `backend` only at startup → 502 after every backend restart/rebuild); `/static` unbuffered (video streaming); Gunicorn `--threads 4` (2×4 concurrent requests, slow AI calls no longer block the site)
- Docker has its OWN database (empty on first start). Local data was copied in with mysqldump + `docker compose cp` of uploads (commands in README). Schema check: DB built from `init_db.sql` == DB built by migrations v1–v9 (8 tables, all columns, 12 FKs identical)

---

### Final review (2026-09-29) — timezone + security & correctness audit ✅
- Time zone: every DB connection uses UTC (`time_zone='+00:00'`), API sends ISO with `+00:00`, browser shows local time; containers log in `TZ=Asia/Jerusalem`
- PDF gaps fixed: editor **hyperlink** button (1e.i), `password_resets` in the ER diagram (1f)
- Bugs fixed: like state lost after refresh (public route now reads the optional session), comment count 0 until opened (counts in feed query), feed tab-switch race + duplicate posts on scroll, profile "no changes" error, HTML error pages breaking the frontend
- Hardening: JSON body/param helpers (`utils/request_helpers.py`), length limits, capped pagination, JSON 404/405/429/500 handlers, ban checked on every request, sessions deleted on password reset, reset email HTML-escaped + no enumeration, rate limits (reset, posts, comments, uploads), upload magic-byte check, media URLs must be our uploads, emails removed from public responses, DOMPurify allowlist + safe links, nginx CSP/X-Frame/nosniff/server_tokens off, pinned requirements, Gunicorn 1 worker × 8 threads (exact in-memory rate limits), `print_db.py` removed
- Tests: `conftest.py` blocks real DB + external APIs + rate limits in tests; 272 passed, 97.9% coverage; ESLint 0 errors; Cypress 10/10 on Docker

## 5. Remaining Phases

### Phase 11: GitHub push + AWS Deployment (done at the end, together with the user)
- Before deploying fix: hardcoded `BACKEND_URL = 'http://localhost:5000'` in SinglePost.jsx, CORS origin `localhost:5173` in app.py, `FRONTEND_URL` for reset links, `init_db.sql` must include migrations v2–v9; nginx `client_max_body_size 51M` for videos; uploads need a persistent volume; agents need their own container running `run_agents.py`
- RDS + EC2/ECS + Docker + Gunicorn + Nginx + SSL

### Optional (3 selected)
1. **Video Integration**: play/pause, auto-play on scroll, video_url on posts
2. **Containerization**: Dockerfile + docker-compose
3. **Responsive Design**: Mobile-first MUI breakpoints

---

## 6. Coding Patterns

### User-Mandated Rules
- **Strict Simplicity**: No over-engineering. Easy to explain and defend.
- **Incremental**: ONE phase at a time. Tests alongside feature code.
- **Pause for Review**: After each phase, STOP and wait for user confirmation.
- **No unnecessary commands**: Let user run manually.

### Backend Patterns
- **Repository**: `conn = get_connection()`, `cursor`, `try/finally` close
- **Service**: Validates, raises `ValidationError`/`NotFoundError`/`AuthError`
- **Controller**: `request.get_json()` → service call → `try/except AppError` → `jsonify`
- **Routes**: Blueprint + `@auth_required` for protected
- **Tests**: AAA pattern, `@patch("services.xxx.function_name")` — patch where the name is **used**, not where it is defined (e.g. `@patch("services.reset_service.send_email")`), otherwise the real function runs.

### Frontend Patterns
- **Services**: `request()`/`get()` from `httpClient.js`, base URL auto-prepended
- **MUI Icons**: ALWAYS `import XxxIcon from '@mui/icons-material/Xxx'` (direct default, NOT barrel)
- **Auth**: `useAuth()` from `AuthContext`
- **Barrel**: Update `services/index.js` for new service files

---

## 7. Test Status

**272 tests, all passing — 97.9% coverage** (fails below 85%) — run: `python -m pytest tests/ --cov`

---

## 8. How to Run

```powershell
# Backend:  cd myReact\backend && python app.py  (port 5000)
# Frontend: cd myReact\my-app  && npm run dev    (port 5173)
# Migration: Get-Content backend\migrate_vX.sql -Raw | & "C:\Program Files\MySQL\MySQL Server 9.6\bin\mysql.exe" -u root -p social_app   (prompts for the password)
# Tests:    cd myReact\backend && python -m pytest tests/ --cov   (coverage report, fails < 85%)
# E2E:      both servers running, then  cd myReact\my-app && npx cypress run
# Agents:   cd myReact\backend && python seed_agents.py   (once)  then  python run_agents.py   (keep running in its own terminal)
```
