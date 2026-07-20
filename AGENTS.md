## Build & Run

**Bootstrap** (first time only):
```bash
script/bootstrap  # Installs Python and Node dependencies
```

**Setup** (first time and after migrations):
```bash
script/setup  # Creates .env, database, runs migrations
```

**Server** (development):
```bash
script/server  # Starts Flask on :5000 + Vite on :5173
```

## Cleanup

Run these slash commands to clean up code:
- `/python-code-simplifier` - Simplifies recently modified Python code for clarity and maintainability while preserving functionality.
- `/typescript-code-simplifier` - Simplifies recently modified TypeScript code for clarity and maintainability while preserving functionality.

## Validation

IMPORTANT ALWAYS RUN these after implementing to get immediate feedback:

- Tests: `script/test` → `pytest` + `vitest`
  - Direct: `PYTHONPATH=src pytest tests/` (backend) + `cd frontend && npm test` (frontend)
- E2E: `script/test-e2e` → Playwright browser tests
  - Direct: `npx playwright test --reporter=list` (auto-starts dev servers; use `--reporter=list` in non-interactive shells — the default `html` reporter opens a blocking report server that hangs CI/agents)
  - First run needs browsers: `npx playwright install chromium`
  - UI mode: `script/test-e2e --ui`
- Typecheck: `script/typecheck` → `mypy` + `tsc`
  - Direct: `mypy src/ --ignore-missing-imports` + `cd frontend && npm run typecheck`
- Lint: `script/lint` → `flake8` + `eslint`
  - Direct: `flake8 src/ tests/` + `cd frontend && npm run lint`

## Local environment (no venv/node_modules committed)

First-time, without the `script/*` helpers (which assume Postgres):
- Backend: `py -3.13 -m venv .venv && .venv/Scripts/python -m pip install -r requirements-dev.txt`
  (project needs Python ≥3.12; flask-sqlalchemy 3.1.1 ships types, so `class Game(db.Model)`
  needs `# type: ignore[misc]` under mypy strict).
- Frontend: `cd frontend && npm install`. Root E2E deps: `npm install` then `npx playwright install chromium`.
- Run checks directly: `.venv/Scripts/python -m pytest tests/ -q`, `... -m mypy src/`,
  `... -m flake8 src/ tests/`; `cd frontend && npm run typecheck|lint|test`.

## E2E on Windows (no local Postgres)

`playwright.config.ts`'s `webServer: script/server` fails under Windows cmd.exe
(`'script' is not recognized`). Instead start the stack manually with a SQLite DB
and let Playwright reuse it (`reuseExistingServer` is true):
```bash
export PATH="$PWD/.venv/Scripts:$PATH" DATABASE_URL="sqlite:///e2e_test.db" FLASK_APP=src/app:create_app
flask db upgrade                                   # create games table in the sqlite file
(cd frontend && npm run dev) &                     # Vite :5173
flask run --host=127.0.0.1 --port=5000 &           # Flask :5000
npx playwright test --reporter=list                # never the default html reporter (it blocks)
```

## Operational Notes

- **Backend**: Flask on :5000, `PYTHONPATH=src` required when running pytest directly
- **Frontend**: Vite dev server on :5173, React Islands pattern with `data-island` attributes in templates
- **Database**: PostgreSQL, connection via `DATABASE_URL` env var (set by `script/setup`)
- **Dev environment**: `.env` created by `script/setup`, contains all runtime config

### Codebase Patterns

- Backend: Python/Flask in `src/`, tests in `tests/`
- Frontend: React in `frontend/`, compiled to static assets
- Templates: Jinja2 with Islands hydration points (`data-island` attributes)
- Migrations: Alembic in `migrations/`, auto-applied by `script/setup`
- E2E tests: Playwright in `e2e/`, config in `playwright.config.ts`

### Browser Testing

A **Playwright MCP server** is configured in `.vscode/mcp.json` for interactive browser testing via agent mode. Use the `/test-in-browser` slash command for the full workflow — it teaches you how to navigate the app, interact with elements, and verify results using accessibility snapshots.


### Commit Messages
Use the slash command `/git-commit` to create well-structured git commits.
