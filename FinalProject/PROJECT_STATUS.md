# SocialApp — Project Status & AI-Agent Handoff

> **Last updated:** 2026-09-29 (≈04:30 Israel time)
> **Read this first.** It tells an AI agent (or developer) exactly what is finished, what is left,
> how to do it, and which mistakes to avoid. Everything except **Phase 11 (AWS deployment)** is DONE.

---

## 0. TL;DR — where we stopped

- **All features, all PDF requirements, 3 optional features, tests, Docker: DONE and verified.**
- **GitHub: DONE (except the newest AWS files).** Branch `FinalProject` pushed to
  https://github.com/benyanev/FullStackDev/tree/FinalProject (project lives in the folder `FinalProject/`).
- **LEFT: Phase 11 — deploy to AWS (EC2 + RDS + free HTTPS domain).** Config files are written
  (`docker-compose.aws.yml`, `Caddyfile`) — committed locally in `myReact`, **not yet pushed and not yet run on AWS**.
- The user took a break in the middle of Phase 11. **On return, first ask the user the open
  questions in §3.1** (they asked to be reminded), then follow §3.

---

## 1. Project overview & locations

**What:** Social media platform (RUNI Full Stack Project 2026 — final project).
**Stack:** React 19 + Vite + MUI (frontend) · Flask 3 REST API (backend) · MySQL · OpenAI · Resend (email) · Docker.
**User:** student (Windows 11, PowerShell 5.1, VS Code). Communicates in English; prefers step-by-step, simple, explainable code.

| What | Where |
|---|---|
| Project (working copy) | `C:\Users\benya\cs\FullStackDev\myReact` (its own small local git repo, branch `main`) |
| GitHub clone (what gets pushed) | `C:\Users\benya\cs\FullStackDev\FullStackDev` → remote `https://github.com/benyanev/FullStackDev.git` (public) |
| Requirements PDF | `myReact\RUNI Full Stack Project 2026 (1).pdf` (git-ignored) |
| EC2 SSH key | `C:\Users\benya\cs\FullStackDev\key_pair_benor.pem` (outside both repos — never commit) |
| Secrets | `myReact\.env` only (git- and docker-ignored). **Never print or commit it.** Keys inside: DB_*, RESEND_API_KEY, OPENAI_API_KEY; commented `# for AWS` lines hold the RDS host/user. |
| Python venv | `myReact\.venv` (use `..\.venv\Scripts\python.exe` from `backend/`) |
| Docker CLI | `C:\Program Files\Docker\Docker\resources\bin` (old terminals may not have it on PATH — restart VS Code) |

**GitHub repo convention:** one folder + one branch per assignment (`HW3`, `HW4`, `HW5`, `HW6`, `HW6.1`, …).
`FinalProject` branch was created from `origin/HW6.1` and adds the folder `FinalProject/` (copy of `myReact`).

---

## 2. Requirements checklist (PDF) — all implemented

| PDF item | Status | Where / notes |
|---|---|---|
| 1a Signup/login/logout, hashed passwords | ✅ | bcrypt, server sessions (UUID in HttpOnly cookie) |
| 1b Profile: name, bio, picture, user's posts | ✅ | `UserProfile/` |
| 1c Search by name, follow/unfollow + lists, "time ago" | ✅ | `Search/`, `useFollow`, `utils/timeAgo.js` (UTC-correct) |
| 1d Global + following feed, infinite scroll | ✅ | `Feed/useFeed.js`, `hooks/useInfiniteScroll.js` |
| 1e Post text + image, WYSIWYG bold/italic/**hyperlinks** | ✅ | Tiptap `NewPost/` (link button in `MenuBar.jsx`) |
| 1f DB diagram | ✅ | `database_schema.md` (Mermaid ER, all 8 tables) |
| 2a Secure password reset by email | ✅ | Resend; one-time token 1h; logs out all sessions |
| 2b Likes + comments | ✅ | |
| 2c Autocorrect, suggested posts, suggested comments | ✅ | `ai_service.py`, `AiAssistBar.jsx`, ✨ in comments |
| 2d ≥10 agents with personalities, continuous | ✅ | 12 agents, `seed_agents.py` + `run_agents.py` |
| 2e Admins, report + dashboard (delete/ban), sentiment block | ✅ | `/admin`, OpenAI Moderation blocks toxic posts/comments |
| 2f 85% coverage | ✅ | **97.9%**, 273 tests; run fails < 85% |
| 3 Optional ×3 | ✅ | Video (custom player + autoplay on scroll), Responsive, Docker |
| 4 Deployed on AWS | ⏳ **Phase 11 — in progress** | see §3 |
| Submission: GitHub link + site URL | ⏳ | GitHub done; URL after AWS |

---

## 3. REMAINING WORK — Phase 11: AWS deployment

**Decisions already made by the user:** EC2 (already running) + **their existing RDS MySQL** + **HTTPS with a free DuckDNS domain**.
**Design (already coded):** on EC2 run `docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d --build`:
- `db` container disabled (profile) → backend/agents use **RDS** (`DB_HOST`/`DB_USER`/`DB_PASSWORD` from `.env`)
- **Caddy** (`Caddyfile`) is the only public entry (80/443), auto Let's Encrypt cert for `$DOMAIN`, HSTS, proxies to nginx (`frontend`)
- `FLASK_ENV=production` (Secure cookie), `PROXY_HOPS=2` (Caddy + nginx → real client IP for rate limits), `FRONTEND_URL=https://$DOMAIN`

### 3.1 Ask the user first (they asked to be reminded)
1. **EC2 OS** — Ubuntu (SSH user `ubuntu`) or Amazon Linux (`ec2-user`)? ("remind me to check it later")
2. **Which data on AWS** — copy local data (users/posts/comments/likes + uploaded images/videos) into RDS, or start fresh (only the 12 bots)? ("remind me and ask me later"). Recommend copying. **Check what RDS `social_app` already contains and tell the user before replacing anything.**
3. **EC2 public IP (ideally an Elastic IP) and DuckDNS domain** (e.g. `socialapp-benor.duckdns.org`).
4. Confirm the manual console steps below are done.

### 3.2 Manual steps the USER must do (websites Claude can't log into)
1. **DuckDNS**: https://www.duckdns.org → sign in → create subdomain → set "current ip" = EC2 public IP.
2. **Elastic IP (recommended)**: EC2 → Elastic IPs → Allocate → Associate with the instance (otherwise the IP changes on stop/start and breaks the domain). Put that IP in DuckDNS.
3. **EC2 security group inbound**: SSH 22 from *My IP*; HTTP 80 + HTTPS 443 from *Anywhere-IPv4* (80 is needed for the Let's Encrypt challenge).
4. **RDS security group inbound**: MySQL 3306 **source = the EC2 instance's security group**. (Verified 2026-09-29: RDS is NOT reachable from the user's PC — correct, keep it that way.)

### 3.3 Step-by-step (Claude does this, with the user's OK)
0. **Publish the latest files first** (the "Phase 11 prep" commit is only local): sync `myReact` into the clone's
   `FinalProject/` folder and push (see §4 "How to publish" — skip its first `git commit` line if nothing changed).
1. **SSH** (Git Bash): `ssh -i /c/Users/benya/cs/FullStackDev/key_pair_benor.pem <user>@<IP>`
   (If "permissions too open": the key must be readable only by the user.)
2. **Install Docker** on the server
   - Ubuntu: `curl -fsSL https://get.docker.com | sudo sh && sudo usermod -aG docker $USER` (log out/in)
   - Amazon Linux 2023: `sudo dnf install -y docker git && sudo systemctl enable --now docker && sudo usermod -aG docker ec2-user`, then install the compose plugin (`~/.docker/cli-plugins/docker-compose` from the docker/compose GitHub releases).
   - **Small instances (t2/t3.micro, 1 GB RAM)**: add swap before building, or `npm ci`/`vite build` can be killed:
     `sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`
3. **Get the code**: `git clone --branch FinalProject --single-branch https://github.com/benyanev/FullStackDev.git && cd FullStackDev/FinalProject`
4. **Create `.env` on the server** (prepare it on the PC from `.env.example`, copy with `scp -i <key> .env.aws <user>@<IP>:~/FullStackDev/FinalProject/.env`; never commit it). Must contain:
   `DB_HOST=<RDS endpoint>`, `DB_USER=admin` (from the commented AWS lines in local `.env`), `DB_PASSWORD`, `DB_NAME=social_app`,
   `SECRET_KEY=<new random: python -c "import os;print(os.urandom(24).hex())">`, `OPENAI_API_KEY`, `OPENAI_MODEL=gpt-4.1-mini`,
   `RESEND_API_KEY`, `EMAIL_FROM`, `DOMAIN=<name>.duckdns.org`, `AGENT_INTERVAL_SECONDS=60`. Make sure it has LF line endings.
5. **Prepare the RDS database** (from the server, e.g. `docker run --rm -it mysql:8.4 mysql -h <RDS> -u admin -p`):
   - Inspect first: `SHOW DATABASES; USE social_app; SHOW TABLES; SELECT COUNT(*) FROM users;` → report to the user.
   - **Fresh**: pipe `backend/init_db.sql` (full current schema) into RDS.
   - **Copy local data** (user's choice): on the PC
     `& "C:\Program Files\MySQL\MySQL Server 9.6\bin\mysqldump.exe" -u root -p --single-transaction --no-tablespaces --set-gtid-purged=OFF social_app --result-file=local_dump.sql`,
     `scp` it to the server, import into RDS (`CREATE DATABASE IF NOT EXISTS social_app` first), delete the dump afterwards.
     If RDS is MySQL 8.x and the dump fails on a 9.x-only feature, report the exact error.
   - An existing RDS schema from an older homework must be upgraded (missing migrations `backend/migrate_v*.sql`) or replaced — ask the user.
6. **Start**: `docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d --build`
   then `docker compose ... logs -f caddy` until the certificate is obtained, and `logs agents` (bots seed themselves).
7. **Uploads** (only if data was copied): `scp -r` the PC's `backend/static/uploads` to the server, then
   `docker compose ... cp uploads/. backend:/app/static/uploads/`.
8. **Admin**: `docker compose -f docker-compose.yml -f docker-compose.aws.yml exec backend python make_admin.py <user email>`
9. **Verify**: `https://<domain>` loads with a padlock; sign up/login works (Secure cookie); post with image/video; comments/likes;
   AI assist; moderation blocks a toxic comment; reset email link points to `https://<domain>` (Resend's test sender only
   delivers to the Resend account owner — the address the Resend account was registered with); bots post; `/admin`.
   From the PC: `npx cypress run --config baseUrl=https://<domain>` (creates `e2e_test_*` users — delete them after).
   Check headers: `curl -sI https://<domain>` (CSP, X-Frame-Options, HSTS).
10. **Finish**: put the live URL in `README.md`, publish again (§4), give the user the two submission links
    (GitHub `…/tree/FinalProject/FinalProject` + `https://<domain>`). Remind them about costs (stop/terminate
    EC2/RDS/Elastic IP after grading) and to keep only one bot runner (local, Docker or AWS) active.

**Known limits to mention if asked:** rate-limit counters are in memory (fine for 1 server process); OpenAI moderation fails
open if OpenAI is down; Resend test sender only reaches the account owner (a verified domain is needed for everyone).

---

## 4. Git / GitHub state and how to publish

- **Local project repo** (`myReact`, branch `main`): `229f30f` (initial), `fefdc5b` (final project, = what is on GitHub),
  then a local commit "Phase 11 prep" with `docker-compose.aws.yml`, `Caddyfile`, PROXY_HOPS (`backend/core/config.py`,
  `backend/app.py`, `backend/tests/test_app.py`) and this file — **committed locally, NOT yet copied to the clone / pushed**.
- **GitHub clone** (`FullStackDev\FullStackDev`): branch `FinalProject` (commit `471f36d`) pushed and tracking `origin/FinalProject`.
- **How to publish changes** (Git Bash; copies only tracked files, so `.env`, `.venv`, `node_modules`, uploads never leave the PC):
  ```bash
  cd /c/Users/benya/cs/FullStackDev/myReact && git add -A && git commit -m "..."
  cd /c/Users/benya/cs/FullStackDev/FullStackDev && git checkout FinalProject
  rm -rf FinalProject && mkdir FinalProject && git -C ../myReact archive HEAD | tar -x -C FinalProject
  git add -A FinalProject && git grep --cached -nE "sk-proj-|re_[0-9A-Za-z]{8}" -- FinalProject   # must print nothing
  git commit -m "..." && git -c http.sslBackend=schannel push
  ```
  (`http.sslBackend=schannel` is needed on this PC — the default OpenSSL backend fails with "unable to get local issuer certificate".)
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (session attribution rule).
- **Never** `git add` the `.env`, the `.pem` key, dumps, or `static/uploads/*` files. History was checked: no secret was ever committed.

---

## 5. How to run (3 ways)

| Mode | Command | URL | Database |
|---|---|---|---|
| Local dev (hot reload) | `backend: python app.py` + `my-app: npm run dev` (+ optional `backend: python run_agents.py`) | http://localhost:5173 | local MySQL 9.6 (`social_app`) |
| Docker on the PC | `docker compose up -d` (`--build` after code changes); stop: `docker compose down` (`-v` deletes data) | http://localhost:8080 | its **own** MySQL container (data was copied from local once; they now drift apart) |
| AWS | §3 | https://<domain> | RDS |

- Tests: `cd backend && ..\.venv\Scripts\python.exe -m pytest tests/ --cov` → **273 passed, 97.9%** (fails < 85%).
- Lint/build: `cd my-app && npx eslint src && npx vite build` (delete `dist/` after) → 0 errors.
- E2E: servers running, `cd my-app && npx cypress run [--config baseUrl=http://localhost:8080]` → 10/10.
- Migrations on local MySQL: all of v1–v9 are applied. New DBs use `backend/init_db.sql` (identical schema, verified).
- Make a moderator: `python make_admin.py <email>` (local) / `docker compose exec backend python make_admin.py <email>`.
- Bot runners: only run ONE (local `run_agents.py`, Docker `agents`, or AWS) — each spends OpenAI credit (user added $10).

---

## 6. Architecture

```
Browser (React 19 / MUI) ── /api/* JSON + HttpOnly cookie, /static/* media
   │   dev: Vite proxy :5173 → Flask :5000
   │   Docker: nginx (frontend container, CSP + security headers) → Gunicorn (1 worker × 8 threads)
   │   AWS: Caddy (HTTPS) → nginx → Gunicorn
Flask: routes (Blueprints + rate limits) → controllers (utils/request_helpers) → services (rules, AppError)
       → repositories (raw SQL, %s params, own connection each, UTC session) → MySQL
Separate process: run_agents.py → agent_service → ai_service + post/comment services (same rules as humans)
External: OpenAI (moderation, chat), Resend (email)
```

**Backend (`backend/`)**: `app.py` (factory, JSON error handlers, ProxyFix, limiter config) ·
`core/` (config from `.env` with `override=True`, database `time_zone='+00:00'`, exceptions incl. ModerationError 422, extensions) ·
`middlewares/auth_middleware.py` (`_check_session` → `auth_required`, `admin_required`, `get_optional_user_id`; banned users rejected on every request) ·
`repositories/` (user, post [like_count/comment_count subqueries], comment, like, follow, session [joins is_banned], reset, report) ·
`services/` (auth [validate_password], user [PRIVATE_FIELDS hidden publicly], post, comment, like, follow, reset, email [Resend], upload [magic bytes], sentiment, ai, agent, admin, report) ·
`utils/` (serializers → UTC ISO, request_helpers, file_helpers [`is_upload_url`]) ·
scripts `seed_agents.py`, `run_agents.py`, `make_admin.py` · `init_db.sql`, `migrate_v2..v9.sql` · `Dockerfile`.

**Frontend (`my-app/src/`)**: `main.jsx` (MUI theme, responsive fonts) · `App.jsx` (routes) · `context/AuthContext` ·
`services/*` (`httpClient.js`: `request`/`get`/`requestFormData`, errors carry `.status`, non-JSON safe) ·
`hooks/` (useInfiniteScroll, useFollow, useAutoPlay) · `components/` (Admin/, Feed/, NewPost/ [MenuBar with link, MediaUploadArea, AiAssistBar],
SinglePost/ [PostBody with DOMPurify allowlist, PostActions, CommentSection, VideoPlayer, ReportDialog], UserProfile/, Users/, User/, Search/,
TopBar + MobileMenu, AgentBadge, ModerationDialog, Login, Signup, ResetRequest, ResetConfirm) · `nginx.conf`, `Dockerfile` · `cypress/e2e/`.

**Database (8 tables):** users (role, is_banned, is_agent, personality), posts (image_url, video_url), sessions, follows, likes, comments, password_resets, reports. See `database_schema.md`.

---

## 7. Coding rules & patterns (follow these)

**User rules:** strict simplicity (easy to explain/defend) · one phase at a time with tests · **pause for review after each phase** ·
explain what the user must run; give **one-line** PowerShell commands · warn at the TOP of a phase if a migration must run first
(new code + old DB = broken site) · deployment-friendly code (settings from env, no hardcoded localhost).

**Backend:** controller = `json_body()`/`get_text()`/`page_params()` → service → `try/except AppError` → `jsonify` ·
services validate (length limits) and raise `ValidationError`/`NotFoundError`/`ForbiddenError`/`ConflictError`/`ModerationError` ·
repositories: `conn = get_connection(); cursor; try/finally close` · new rate-limited routes: `@limiter.limit(...)` above `@auth_required` ·
public data must not include email/role/is_banned.

**Tests:** pytest, AAA, `@patch` where the name is **used** (e.g. `services.reset_service.send_email`).
`tests/conftest.py` autouse fixtures: blank RESEND/OPENAI keys, **disable rate limits** (`app.RATELIMIT_ENABLED`), and
**block real DB connections** (`mysql.connector.connect` raises) — a test that forgets a mock fails instead of touching the user's DB.

**Frontend:** services via `httpClient.js`; MUI icons imported directly (`@mui/icons-material/Xxx`); `useAuth()`;
data fetching in effects uses `.then()` chains (ESLint `react-hooks/set-state-in-effect`); outdated requests ignored via a request-id ref (see `useFeed.js`).

---

## 8. Gotchas learned on this PC (read before running commands)

- **PowerShell splits long pasted commands** onto a `>>` line → give short one-line commands; when the user's terminal fails, Claude can run DB migrations via the venv Python (`core.database.get_connection()`).
- PowerShell 5.1 mangles nested quotes for native exes (`mysql -e "…'…'…"`) → use scripts (`make_admin.py`) or `Get-Content file -Raw | …`.
- A **Windows-level `OPENAI_API_KEY`** (User + Machine env vars, old key) existed → `load_dotenv(..., override=True)` in `core/config.py` makes `.env` win. Don't remove the override.
- OpenAI: moderation is free; chat needs credits (user added $10). Model `gpt-4.1-mini`.
- Resend test sender (`onboarding@resend.dev`) only delivers to the account owner's address.
- Git Bash heredocs turn `\x89`-style escapes into raw bytes when editing via Python heredoc → write such files with the Write tool.
- nginx must resolve `backend` via `resolver 127.0.0.11` + variable (`set $backend`), otherwise 502 after every backend restart.
- `package-lock.json` must stay in sync (Docker uses `npm ci`, Node 24 image = local Node 24).
- Docker has its own DB — "posts missing" in Docker means data wasn't copied, not a bug.
- All times are UTC in DB/API; containers use `TZ=Asia/Jerusalem` only for logs.

---

## 9. History of completed phases (short)

1. **Likes & comments** · 2. **Password reset** (Resend, UTC, enumeration-safe) · 3. **Admin & reports** (`migrate_v7`) ·
4. **Moderation** (OpenAI, 422 → ModerationDialog) · 5. **AI assist** (autocorrect, write post, suggest comment) ·
6. **12 AI agents** (`migrate_v8`, seed + runner, 🤖 badge) · 7. **Tests 85% → 97.9%** (table-driven repo tests, conftest guards) ·
8. **Video** (`migrate_v9`, custom player, autoplay on scroll) · 9. **Responsive** (MobileMenu, admin cards on phones, Cypress checks) ·
10. **Docker** (compose: db/backend/agents/frontend, init_db.sql = full schema, nginx) ·
**Final review 2026-09-29**: UTC timestamps; hyperlink button; ER diagram complete; fixed like state after refresh, comment counts,
feed race/duplicates; hardening (JSON errors, input limits, ban check per request, reset logs out sessions, rate limits, upload magic bytes,
private emails, DOMPurify allowlist, CSP/security headers, pinned deps); GitHub branch `FinalProject` pushed ·
**Phase 11 started:** AWS override + Caddy HTTPS + PROXY_HOPS written and validated with `docker compose config` (not deployed yet).
