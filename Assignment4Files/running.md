# Running the Application

This repository contains a **Minesweeper** web game built with a Flask
backend and a React Islands frontend. It supports selectable difficulty
presets (Beginner / Intermediate / Expert) and a persistent high-score
leaderboard that shows up when a player beats the game. It records the
time it took for them to solve the game and the lowest time gets ranked
the highest. There are different leaderboard states for every 

In development the app runs as **two servers**:

- **Flask** (backend + HTML) on `http://localhost:5000` — this is the URL you open in the browser.
- **Vite** (frontend dev server) on `http://localhost:5173` — Flask hydrates the React islands from here.

## Windows (PowerShell, using SQLite)

The `script/*` helpers are bash/Linux-oriented, so on Windows run the servers
directly. Using **SQLite** avoids needing a PostgreSQL server — the migrations
are SQLite-compatible.

**Prerequisites:** Python 3.12+ and Node 20+. (A `.venv/` is already bundled in the repo.)

### One-time setup

```powershell
# 1. Create your .env from the template
Copy-Item .env.example .env

# 2. Install Python dependencies into the bundled virtualenv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt

# 3. Install frontend dependencies
cd frontend; npm install; cd ..

# 4. Create the SQLite database schema (file at src/instance/dev.db)
$env:DATABASE_URL = "sqlite:///dev.db"
$env:FLASK_APP = "src/app:create_app"
.\.venv\Scripts\python.exe -m flask db upgrade
```

> **Tip:** add `DATABASE_URL=sqlite:///dev.db` to your `.env` so you don't have
> to set `$env:DATABASE_URL` in each terminal.

### Start the servers (two terminals)

```powershell
# Terminal 1 — Vite (frontend) on http://localhost:5173
cd frontend; npm run dev
```

```powershell
# Terminal 2 — Flask (backend) on http://localhost:5000
$env:DATABASE_URL = "sqlite:///dev.db"
$env:FLASK_APP = "src/app:create_app"
$env:FLASK_DEBUG = "1"
.\.venv\Scripts\python.exe -m flask run --host=0.0.0.0 --port=5000
```

Then open **http://localhost:5000**.

> **Prefer PostgreSQL on Windows?** Start your local PostgreSQL, create an
> `app` database, and set
> `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app` in `.env`
> (then skip the `$env:DATABASE_URL` lines above).
