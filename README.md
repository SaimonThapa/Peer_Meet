# CSC 489 Social Media Security Lab - Peer Meet

This repository contains an Instagram-inspired social media web application for the CSC 489 web security capstone. It is a local educational lab, not a production website. The app is meant to work like a small social network while also containing a limited set of intentional security weaknesses for classroom demonstration.

The project was built end to end with an automated coding workflow, so this README explains both what users see in the app and what is happening under the hood.

## Plain-English Overview

The app lets demo users:

- Sign up and sign in.
- View a global feed of image posts.
- Create a single-image post with an optional caption.
- Like and comment on posts.
- View public profiles.
- Follow and unfollow users.
- Search for users and posts.
- Use a basic admin dashboard when signed in as an admin.

For the security class, the app also includes intentionally vulnerable behavior. These weaknesses are only for local, synthetic lab testing. Do not put this app on the public internet.

## Important Safety Notice

This project is intentionally vulnerable in specific places. It must be run only on a local or isolated lab machine with fake accounts and disposable data.

Do not use:

- Real personal information.
- Real passwords used anywhere else.
- Real email accounts.
- Public hosting or tunnels.
- Production databases.

The allowed vulnerabilities are documented in `docs/VULNERABILITIES.md`. Do not add extra vulnerabilities or silently remove the approved ones unless the assignment asks for remediation.

## Tech Stack

Frontend:

- Next.js App Router
- JavaScript and JSX
- Tailwind CSS
- React Context for authentication state

Backend:

- Python Flask
- SQLite using Python's built-in `sqlite3`
- JWT access and refresh cookies
- bcrypt password hashing
- Image uploads stored as SQLite BLOBs

Testing and documentation:

- Pytest for backend smoke tests
- Manual browser testing with the running frontend and backend
- QA notes in `docs/QA_REPORT.md`
- Security test notes in `docs/SECURITY_TESTS.md`

## Seeded Demo Accounts

The backend creates these accounts automatically when the SQLite database is first initialized.

| Role | Username | Password | Display Name | Purpose |
| --- | --- | --- | --- | --- |
| Admin | `admin` | `AdminPass123!` | Admin Simon | Admin dashboard and moderation demos |
| User | `alice` | `Password123!` | Alice Wonderlands | Normal user and login demo |
| User | `bob` | `Password123!` | Bob  | Normal user and profile/security demos |
| User | `sagun` | `Password123!` | Sagun Ghimire | Extra normal user for social flows |

Recommended first login:

```text
username: alice
password: Password123!
```

Admin login:

```text
username: admin
password: AdminPass123!
```

## Repository Structure

```text
social-security-lab/
  AGENTS.md
  README.md
  docs/
    PRODUCT.md
    DESIGN.md
    ARCHITECTURE.md
    VULNERABILITIES.md
    TESTING.md
    IMPLEMENTATION_PLAN.md
    QA_REPORT.md
    SECURITY_TESTS.md
  backend/
    main.py
    requirements.txt
    .env.example
    app/
      auth/
      config/
      controllers/
      logger/
      models/
      routes/
      schemas/
    migrations/
    tests/
    instance/
  frontend/
    package.json
    .env.local.example
    src/
      app/
      api/
      components/
      context/
      features/
      layouts/
      lib/
```

### Main Folders

`docs/`

Contains the product, architecture, design, testing, and security-lab specifications. Read these files before making major changes.

`backend/`

Contains the Flask API, SQLite setup, routes, authentication helpers, seed data, migrations, and backend tests.

`frontend/`

Contains the Next.js user interface, API client, auth context, routes, layout, and reusable UI components.

## How the App Works

The frontend and backend run as two separate local servers.

The browser opens the frontend at:

```text
http://localhost:3000
```

The frontend sends API requests to the Flask backend at:

```text
http://localhost:5000/api/v1
```

The backend owns the database. The frontend never reads SQLite directly.

Authentication uses browser cookies. The access token and refresh token are stored as HttpOnly cookies, which means normal frontend JavaScript cannot read them. If an access token expires, the frontend API client tries one refresh request and then retries the original request once.

Uploaded images are stored in SQLite as BLOB data. Feed responses return image URLs instead of embedding image bytes directly in JSON.

## First-Time Setup

Run the backend and frontend in two separate terminals.

### 1. Backend Setup

From the repository root:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If you are using Git Bash, you can still run the Windows Python path:

```bash
cd backend
./.venv/Scripts/python.exe -m pip install -r requirements.txt
```

### 2. Frontend Setup

From the repository root:

```powershell
cd frontend
cmd /c npm install
```

In Git Bash:

```bash
cd frontend
npm install
```

## Running the Project

### Terminal 1: Start the Backend

```powershell
cd backend
.\.venv\Scripts\python.exe main.py
```

Expected backend address:

```text
http://127.0.0.1:5000
```

Health check:

```text
http://localhost:5000/api/v1/health
```

### Terminal 2: Start the Frontend

```powershell
cd frontend
cmd /c npm run dev
```

In Git Bash:

```bash
cd frontend
npm run dev
```

Expected frontend address:

```text
http://localhost:3000
```

Open the frontend in your browser and sign in with one of the seeded accounts.

## Normal User Guide

1. Open `http://localhost:3000`.
2. Select `Sign in`.
3. Log in as `alice` with `Password123!`.
4. View the global feed.
5. Use `Search` to find users or post captions.
6. Use `Post` to upload one file and write an optional caption.
7. Open a profile to follow or unfollow another account.
8. Open a post to like or comment.
9. Use `Profile` or `Settings` to edit your public profile fields.

Admin users can open the admin dashboard from the navigation after signing in as `admin`.

## Developer Guide

### Backend Commands

Install dependencies:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run backend:

```powershell
cd backend
.\.venv\Scripts\python.exe main.py
```

Run backend tests:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest --basetemp=.pytest-tmp
```

The `--basetemp=.pytest-tmp` option keeps pytest temporary files inside the repository folder. This avoids Windows temp-folder permission issues.

### Frontend Commands

Install dependencies:

```powershell
cd frontend
cmd /c npm install
```

Run frontend:

```powershell
cd frontend
cmd /c npm run dev
```

Build frontend:

```powershell
cd frontend
cmd /c npm run build
```

Clean frontend build cache:

```powershell
cd frontend
cmd /c npm run clean
```

The `dev` script already runs `clean` first because this project is stored inside OneDrive, and Next.js cache files can become stale or corrupted there.

## Environment Files

Examples are provided:

- `backend/.env.example`
- `frontend/.env.local.example`

Actual local environment files are ignored by Git:

- `backend/.env`
- `frontend/.env.local`

The default setup works without creating local environment files.

Backend default frontend origins:

```text
http://localhost:3000
http://127.0.0.1:3000
```

Frontend default API base URL:

```text
http://localhost:5000/api/v1
```

## Data and Database Notes

The SQLite database is created locally under `backend/instance/`.

That folder is ignored by Git because it contains generated local data. If you delete the database file, the app will recreate the schema and seed data the next time the backend starts.

Seed data includes:

- Four synthetic users.
- Three synthetic posts.
- One follow relationship.
- One like.
- One comment.

Do not commit real database files.

## Intentional Security-Lab Behavior

This app contains approved vulnerabilities for the capstone. They are tracked in `docs/VULNERABILITIES.md`.

The approved categories are:

- SQL injection in login.
- Stored XSS in comments.
- Reflected XSS in search query display.
- Broken admin authorization for selected admin endpoints.
- Predictable lab session identifier behavior.
- IDOR for selected public profile fields.
- CSRF on the follow action.
- File upload type and size weaknesses in the lab upload path.

These are not bugs to casually fix during normal cleanup. They are part of the learning lab. If you are working on security remediation, document the change clearly and update the related tests and notes.

Security test evidence belongs in:

```text
docs/SECURITY_TESTS.md
```

Functional QA notes belong in:

```text
docs/QA_REPORT.md
```

## Common Troubleshooting

### Flask says `No module named 'flask'`

You are probably running Python outside the virtual environment.

Use:

```powershell
cd backend
.\.venv\Scripts\python.exe main.py
```

If `.venv` does not exist, create it:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Frontend says port 3000 is already in use

Something is already running on port `3000`.

Find it:

```powershell
netstat -ano | findstr :3000
```

Stop it:

```powershell
taskkill /PID <PID_FROM_NETSTAT> /F
```

Then restart:

```powershell
cd frontend
cmd /c npm run dev
```

### Browser shows CORS errors

Make sure you opened the frontend at exactly:

```text
http://localhost:3000
```

Also restart the backend after changing CORS settings:

```powershell
cd backend
.\.venv\Scripts\python.exe main.py
```

Do not use the Network URL shown by Next.js, such as `http://10.x.x.x:3000`, unless you also add that exact origin to the backend CORS allowlist.

### Next.js reports missing files inside `.next`

The Next.js build cache is stale or corrupted.

Run:

```powershell
cd frontend
cmd /c npm run clean
cmd /c npm run dev
```

The dev script already cleans `.next` before starting.

### PowerShell blocks `npm`

Use:

```powershell
cmd /c npm run dev
```

instead of:

```powershell
npm run dev
```

### OneDrive causes cache problems

The project currently lives in a OneDrive folder. Next.js and Python caches sometimes behave badly in synced folders.

If cache errors keep returning, move the repository to a local non-synced folder such as:

```text
C:\Projects\social-security-lab
```

Then reinstall dependencies or reuse the same commands from this README.

## What Should Be Committed

Commit:

- Source code.
- Documentation.
- Migration files.
- Test files.
- Example environment files.
- Package lock files.

Do not commit:

- `.env` files.
- SQLite database files.
- `node_modules`.
- `.next`.
- `.venv`.
- Python cache folders.
- Local screenshots or generated QA artifacts unless the team intentionally wants to keep them as evidence.

The `.gitignore` files at the root, backend, and frontend levels are set up to help with this.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

## Key Documentation Files

Read these files for deeper project details:

- `docs/PRODUCT.md`: feature requirements and user journeys.
- `docs/ARCHITECTURE.md`: technical structure and API design.
- `docs/DESIGN.md`: UI and responsive design expectations.
- `docs/VULNERABILITIES.md`: approved lab vulnerabilities and boundaries.
- `docs/TESTING.md`: QA and security verification process.
- `docs/IMPLEMENTATION_PLAN.md`: implementation checklist.
- `docs/QA_REPORT.md`: functional QA notes.
- `docs/SECURITY_TESTS.md`: security lab evidence.

## Project Status

The current app has a working first version of the main social network flow:

- Seeded login.
- Global feed.
- Image-backed posts.
- Likes and comments.
- Profiles.
- Follow and unfollow API support.
- Search.
- Admin listing and post deletion endpoints.
- Documented security-lab hooks.

Some areas still need deeper browser QA and security evidence before the capstone can be considered fully complete. Track that work in `docs/IMPLEMENTATION_PLAN.md`, `docs/QA_REPORT.md`, and `docs/SECURITY_TESTS.md`.
