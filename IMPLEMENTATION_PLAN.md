# Implementation Plan — ralph-wiggum-tutorial

## Status

> **Overall: ~40% Complete — Infrastructure done, presentation content unimplemented**

The Flask/React backend infrastructure is fully operational (all 12 backend + 4 frontend tests pass). The **primary deliverable** — a 46+ slide reveal.js presentation on "Getting Good LLM Results" (per `specs/specs.md`) — is currently a 3-slide placeholder in `presentation/index.html`.

---

## 🔴 PRIORITY ITEMS (Not Yet Implemented)

### P0-A: Presentation Slides — Sections 1–9 (Slides 1–25)

Replace the 3 placeholder slides with proper spec content. Build as `<section>` groups with vertical nesting per spec.

- **Section 1: Title + Agenda** (Slides 1–2)
  - Title: "Getting Good LLM Results", subtitle: "A practical guide to agentic AI development"
  - Agenda bullets: Context Window, The Right Tool, Determinism + Non-Determinism, Ensuring Completion
- **Section 2: Long Running AI Work Types** (Slides 3–4)
  - Title: "What do agents do all day?"
  - List with icons: Building, Debugging, Testing, Validation, Performance
- **Section 3: Agents Intro** (Slides 5–8)
  - Definition of agents
  - Code block: `.github/agents/plan-agent.md` frontmatter + key sections (file exists, 105 lines)
  - Our agents list: plan-agent, plan-reviewer
  - Principles: never write a prompt twice, keep small/focused, don't aim for exact, like experts
- **Section 4: Vector Spaces & Agent Focus** (Slides 9–12)
  - Research citations: Kong et al. NAACL 2024, Xu et al. 2023, Salewski et al. NeurIPS 2023, Zou et al. 2023
  - Mechanism causal chain diagram (text-based flow)
  - Anthropic proof: Scaling Monosemanticity May 2024, Arditi et al. 2024
- **Section 5: Skills Intro** (Slides 14–18)
  - Definition of skills
  - Code block: `.github/skills/git-commit/SKILL.md` (file exists, 189 lines)
  - Code block: python-code-simplifier deterministic commands (file exists, 63 lines)
  - All 4 skills listed
  - Abstraction diagram: Agent + Skill + Tools = Full-service prompt
- **Section 6: Mixing Determinism & Non-Determinism** (Slides 19–20)
  - Skills/agents = vague (non-deterministic), tasks = exact tools (deterministic)
  - Even experts use tools — give AI tools
- **Section 7: Environment Abilities** (Slide 21)
  - CLI = full service, ⚠️ dangerous without sandbox
- **Section 8: Hooks** (Slides 22–23)
  - Determinism in agent lifecycle
  - Examples: linters, security agents, chain validation
- **Section 9: The CLI** (Slides 24–25)
  - Most dev tools offer CLI, combine with shell tools, SDKs, frameworks

### P0-B: Presentation Slides — Sections 10–17 (Slides 26–46)

- **Section 10: The Crack Down** (Slide 26)
  - Token cost crackdown, caching, "get rate limited every day"
- **Section 11: Giving Your Agent Tools** (Slides 27–29)
  - Tools list: Linters, Test tools, Playwright, HAR, Flame graphs, Memory profilers, Logging, Write your own
  - Code example: `.vscode/mcp.json` (file exists, 11 lines)
  - Key insight: "If an agent can see it, it can use it"
- **Section 12: Context Window** (Slide 30)
  - "Your best friend and worst enemy"
- **Section 13: Valley of Meh** (Slides 31–34)
  - Context sizes table (Claude 1M, GPT-4o 128K, Gemini 1M)
  - "Lost in the Middle" U-shaped curve diagram
  - Implications: keep context small, put instructions at END (30% improvement)
- **Section 14: Goldilocks Approach** (Slides 35–37g)
  - "Same Task More Tokens" research (Levy et al. ACL 2024)
  - Mimic training set: Markdown, XML tags, few-shot
  - Anthropic best practices: 8 quoted principles (exact quotes in spec)
  - Research quotes: 5 citations with exact quotes
  - Diversity of thought: multi-model debate research + practical table (plan=Opus, search=Sonnet, review=different provider)
- **Section 15: Ralph Loop** (Slides 38–43)
  - Show `loop.sh` overview (file exists, 117 lines)
  - Core loop code snippet (copilot invocation + git push + completion check)
  - Two modes: plan vs build
  - Build prompt key elements from `PROMPT_build.md` (file exists, 21 lines)
  - "Why this uses every best practice" 10-row table
  - Elegant insight: clear context window, re-anchor every step, persistent files
- **Section 16: Agentic SDLC** (Slides 44–45)
  - 11-step numbered list
  - Key principle: multiple agents, deterministic validation between steps
- **Section 17: Closing** (Slide 46)
  - Thank You / Questions

### P0-C: Interactive D3.js Visualization (Slide 13)

- Add D3 v7 via CDN (`cdn.jsdelivr.net/npm/d3@7`) — NOT currently in `presentation/package.json`
- Full-slide embedded scatter plot with dark background (#0d1117)
- 4 persona buttons: 🔐 Security Engineer | 💻 Developer | 📊 Product Manager | 🎓 Educator
- 13 concept points with pre-computed 2D coordinates per persona
- `switchPersona()` function with 800ms `d3-transition` animations
- Convex hulls via `d3-polygon` for cluster boundaries
- Tooltips on hover with concept name + cluster label
- Dracula-compatible color scheme

### P1: Code Examples — Inline Content from Real Files

All referenced files exist and are populated. Implementation means extracting key snippets and embedding as `<pre><code>` blocks with reveal.js highlight plugin:

- Slide 6: `.github/agents/plan-agent.md` frontmatter + key sections
- Slide 15: `.github/skills/git-commit/SKILL.md` YAML frontmatter + workflow
- Slide 16: python-code-simplifier showing lint/mypy/test deterministic commands
- Slide 28: `.vscode/mcp.json` Playwright MCP tool config
- Slide 39: `loop.sh` core loop code snippet
- Slide 41: `PROMPT_build.md` key elements summary

### P2: Reveal.js Configuration & Polish

- Add `data-background` colors for section title/divider slides
- Proper vertical slide nesting (`<section><section>...</section></section>`)
- Verify Highlight plugin renders code blocks with syntax highlighting (monokai theme already linked)
- Speaker notes via `<aside class="notes">` for presenter guidance

### P3: Cosmetic / Low Priority

- Fix typo in folder name: `.github/skills/python-code-simiplifier/` → `python-code-simplifier/`
  - Would require updating any references in specs and AGENTS.md

---

## ✅ COMPLETED ITEMS

### Infrastructure (Flask/React App) — 100% Complete
- ✅ `.devcontainer/` — Python 3.12, PostgreSQL, Node.js with post-create hook
- ✅ `src/app/` — Flask app factory, models, views, templates, errors, logging, schemas, controllers
- ✅ `frontend/` — React Islands, Vite, TypeScript, Tailwind, ESLint, Vitest
- ✅ `scripts/` — bootstrap, setup, server, test, lint, typecheck, update, console, db-seed, Procfile
- ✅ `tests/` — 12 backend tests passing (conftest.py, test_hello.py)
- ✅ `frontend/tests/` — 4 frontend tests passing (HelloIsland.test.tsx)
- ✅ `migrations/` — Alembic initialized with hello table migration
- ✅ `.github/workflows/ci.yml` — CI pipeline
- ✅ `.pre-commit-config.yaml` — Pre-commit hooks
- ✅ Config files — `.gitignore`, `.env.example`, `requirements.txt`, `pyproject.toml`

### Documentation — Complete
- ✅ `AGENTS.md` — Operational commands for build/run/test
- ✅ `README.md` — Project overview, setup, loop explanation, tech stack

### Presentation Skeleton — Complete
- ✅ `presentation/package.json` — reveal.js ^6.0.1 dependency
- ✅ `presentation/index.html` — Basic structure with Dracula theme, plugins loaded
- ✅ Reveal.js + plugins installed in `presentation/node_modules/`

### Ralph Loop Infrastructure — Complete
- ✅ `loop.sh` — Fully functional (117 lines), modes, max iterations, completion promise
- ✅ `PROMPT_plan.md` — Plan mode prompt (22 lines)
- ✅ `PROMPT_build.md` — Build mode prompt (21 lines)
- ✅ `.github/agents/plan-agent.md` — Plan agent definition (105 lines)
- ✅ `.github/agents/plan-reviewer.md` — Plan reviewer definition (20 lines)
- ✅ `.github/skills/` — All 4 skills defined (git-commit 189L, python-code-simiplifier 63L, test-in-browser 102L, typescript-code-simplifier 62L)
- ✅ `.vscode/mcp.json` — Playwright MCP server config (11 lines)

---

## Implementation Notes

- **No `src/lib/` directory** — project uses `src/app/` as the backend module
- **No TODO/FIXME/HACK markers** — codebase is clean
- **All tests green** — 12 backend + 4 frontend, no skipped/flaky tests
- **All files referenced in spec exist** — agents, skills, loop.sh, prompts all populated
- **D3.js not yet added** — needs CDN link in presentation/index.html (not a package.json dep per spec)
- **Presentation is the sole remaining deliverable** — all infrastructure work is done
- **Recommended build order**: P0-A → P0-B → P1 (code examples integrate with slides as they're built) → P0-C (D3 viz is self-contained) → P2 (polish pass)
