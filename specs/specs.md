# Presentation Slide Plan: "Getting Good LLM Results"

## File Locations

The presentation lives in the `presentation/` directory:

| File | Purpose |
|------|---------|
| `presentation/index.html` | **Main slide deck** — all reveal.js slides live here as `<section>` elements |
| `presentation/package.json` | Dependencies (reveal.js ^6.0.1) |
| `presentation/node_modules/reveal.js/` | Reveal.js framework (already installed) |

### Reveal.js Structure
- Each slide = a `<section>` tag inside `<div class="slides">`
- Nested `<section>` tags create vertical slide groups (press ↓ to navigate)
- Theme: `node_modules/reveal.js/dist/theme/dracula.css` (already linked)
- Code highlighting: `node_modules/reveal.js/dist/plugin/highlight/monokai.css`
- Plugins loaded: RevealHighlight, RevealNotes, RevealMarkdown

### Key Repo Files Referenced in Slides
| File | Used In |
|------|---------|
| `.github/agents/plan-agent.md` | Slide 6 — agent file example |
| `.github/agents/plan-reviewer.md` | Slide 7 — our agents list |
| `.github/skills/git-commit/SKILL.md` | Slide 15 — skill file format |
| `.github/skills/python-code-simiplifier/SKILL.md` | Slide 16 — deterministic code in skills |
| `.github/skills/test-in-browser/SKILL.md` | Slide 17 — skills list |
| `.github/skills/typescript-code-simplifier/SKILL.md` | Slide 17 — skills list |
| `loop.sh` | Slides 38-43 — Ralph Loop section |
| `PROMPT_build.md` | Slide 41 — build prompt content |
| `PROMPT_plan.md` | Slide 40 — plan mode |
| `IMPLEMENTATION_PLAN.md` | Slide 43 — persistent memory across loops |
| `AGENTS.md` | Slide 43 — operational context file |
| `.vscode/mcp.json` | Slide 28 — Playwright MCP tool example |

### How to Run the Presentation
```bash
cd presentation
# Option 1: Use reveal.js built-in server (if available)
npx reveal-md index.html
# Option 2: Any static file server
npx serve .
# Option 3: Python
python -m http.server 8000
```

---

## Overview
Transform the user's outline into a reveal.js presentation with ~40+ slides organized into major sections. The presentation uses the Dracula theme on reveal.js with code highlighting. Includes an interactive D3.js vector space visualization.

---

## Slide Breakdown

### Section 1: Getting Good LLM Results — What We Will Cover (Title + Agenda)

**Slide 1 — Title Slide**
- "Getting Good LLM Results"
- Subtitle: "A practical guide to agentic AI development"

**Slide 2 — Agenda Overview**
- Bullet list of topics:
  - Context Window
  - The Right Tool
  - Determinism Mixed with Non-Determinism
  - Ensuring Completion

---

### Section 2: Long Running AI Work Types

**Slide 3 — Long Running AI Work Types (title)**
- Header + brief intro: "What do agents do all day?"

**Slide 4 — Work Types List**
- Building
- Debugging
- Testing
- Validation
- Performance
- Each with a brief one-liner and an icon/emoji

---

### Section 3: Agents Intro

**Slide 5 — What Are Agents? (title)**
- Definition: autonomous AI workers that take instructions, use tools, and iterate toward a goal

**Slide 6 — Show an Agent File**
- Code block showing `.github/agents/plan-agent.md` frontmatter + key sections
- Highlight the YAML frontmatter format (`name`, `description`)

**Slide 7 — Our Agents**
- List all agents in this repo:
  - `plan-agent` — Plans features, spawns sub-agents for research, creates implementation specs
  - `plan-reviewer` — Reviews plans for completeness, checks packages, validates test strategy

**Slide 8 — How to Make Agents: Principles**
- Never write a prompt twice
- Keep them small and focused
- Don't aim for exact — give it a direction
- Like experts: DBA, Planner, Developer, Security Engineer

---

### Section 4: Vector Spaces & Agent Focus

**Slide 9 — A Note on Vector Matrices and Agent Focus (title)**
- "Why persona framing actually works — it's not metaphorical"

**Slide 10 — The Research**
- Key citations:
  - "Role-Play Prompting" (Kong et al., NAACL 2024) — AQuA accuracy: 53.5% → 63.8%
  - "ExpertPrompting" (Xu et al., 2023) — ExpertLLaMA at 96% of ChatGPT
  - "In-Context Impersonation" (Salewski et al., NeurIPS 2023 Spotlight)
  - "Representation Engineering" (Zou et al., 2023) — 36+ behaviors controlled via vectors

**Slide 11 — The Mechanism (causal chain diagram)**
- Text-based flow diagram:
  ```
  Terminology Choice → Token Embedding → Attention Circuits →
  Residual Stream → Sparse Feature Activation → Output Distribution
  ```
- Key insight: "security engineer" literally activates different neural features than "software developer"

**Slide 12 — Anthropic's Proof**
- "Scaling Monosemanticity" (Anthropic, May 2024) — found features for "code with security vulnerabilities" vs "abstract discussion of security"
- "Refusal in Language Models Is Mediated by a Single Direction" (Arditi et al., 2024) — complex behaviors live in 1D subspaces

**Slide 13 — Interactive D3 Visualization**
- Full-slide embedded D3.js scatter plot
- Buttons: 🔐 Security Engineer | 💻 Developer | 📊 Product Manager | 🎓 Educator
- Points animate between persona-specific cluster positions
- Convex hulls show cluster regions with labels
- Dark background (#0d1117) with Dracula-compatible colors
- Implementation: pre-computed 2D coordinates, d3-transition for animation, d3-polygon for hulls

---

### Section 5: Skills Intro

**Slide 14 — What Are Skills? (title)**
- Definition: reusable, structured workflows that combine deterministic steps with AI reasoning

**Slide 15 — Show a Skills File Format**
- Code block from `.github/skills/git-commit/SKILL.md`
- Highlight: YAML frontmatter (`name`, `description`, `allowed-tools`) + workflow steps

**Slide 16 — Show Deterministic Code in Skills**
- Example from the python-code-simplifier showing how it runs `scripts/lint`, `scripts/mypy`, `scripts/test`
- Point: skills embed deterministic validation commands

**Slide 17 — Our Skills**
- List:
  - `git-commit` — AI-generated commits with git notes for reasoning
  - `test-in-browser` — Playwright MCP browser testing workflow
  - `python-code-simplifier` — Refines Python code, runs lint/mypy/tests
  - `typescript-code-simplifier` — Refines TS code, runs lint/typecheck

**Slide 18 — Skills as Abstraction Over Agents**
- Diagram: Agent + Skill + Tools = Full-service prompt
- Skills are the "abilities an expert possesses"
- Agents are the "expert identity"
- Tools are the "equipment they use"

---

### Section 6: Mixing Determinism and Non-Determinism

**Slide 19 — Title: Certainty in an Uncertain World**

**Slide 20 — The Spectrum**
- Skills and agents are vague (non-deterministic)
- Tasks have exact ways to do things (deterministic tools)
- Even experts use tools — give your AI tools
- Makes up for what agents cannot do well (math, exact formatting, file operations)

---

### Section 7: Environment Abilities

**Slide 21 — Environment Abilities**
- Depends on where the agent is running
- CLI = full service (can do anything in the environment)
- ⚠️ This can be dangerous — use a sandbox

---

### Section 8: Hooks Intro

**Slide 22 — Hooks: Determinism in the Agent Lifecycle**
- Hooks run things deterministically during the agent lifecycle
- Results feed back into the agent

**Slide 23 — Hook Examples**
- Run linters every time an agent completes its work
- Have security agents validate other agents' work
- Chain validation: agent A builds → hook runs tests → agent B reviews

---

### Section 9: The CLI

**Slide 24 — The CLI (title)**
- Most modern dev tools offer a CLI version
- Run the LLM in a terminal = very powerful tools

**Slide 25 — CLI Power**
- Full suite of args available
- Combine with shell tools (pipes, scripts, automation)
- Some companies have SDKs for even more access
- Frameworks for complex agent/skill setups

---

### Section 10: The Crack Down

**Slide 26 — The Crack Down ⚡**
- Companies cracking down on usage — long-running agents cost massive $$
- Token optimization is critical
- Lean into caching extensions
- "Get rate limited every day" (badge of honor)

---

### Section 11: Giving Your Agent Tools

**Slide 27 — Give Your Agent Every Tool (title)**
- "Find every programmatic tool you can"

**Slide 28 — The Tools List**
- Linters | Test tools | Browser tools (Playwright)
- HAR files | Flame graphs | Memory profilers
- Logging | Write your own tools
- "Everything"

**Slide 29 — The Key Insight**
- "If an agent can see it, it can use it"
- "If it can't see it, it's working blind and will just try to read code"
- "If an agent can make requests, it can use them to debug or test"

---

### Section 12: The Context Window

**Slide 30 — The Context Window (title)**
- "Your best friend and worst enemy"

**Slide 31 — Context Window Sizes (2025)**
- Table:
  - Claude Opus 4.7: 1,000,000 tokens (~750k words, ~10 novels)
  - GPT-4o: 128,000 tokens (~96k words, ~4 novels)
  - Gemini 2.5 Pro: 1,048,576 tokens (~1M context)
- "About the size of a 1970's Star Wars script" (A New Hope script ≈ 15-25k words, fitting in the smaller windows)

---

### Section 13: The Valley of Meh

**Slide 32 — The Valley of Meh (title)**
- Research: "Lost in the Middle" (Liu et al., Stanford/Meta, 2023, TACL)

**Slide 33 — The U-Shaped Curve**
- Visual: ASCII or simple diagram showing attention drops in the middle
- "Performance is highest at the beginning and end of context"
- "Moving relevant info from position 1 to middle dropped accuracy by 20+ percentage points"

**Slide 34 — Implications**
- You don't know where the valley is, but keep context small
- The more context you're working with, the larger the valley
- Put instructions at the END (Anthropic: "up to 30% improvement")

---

### Section 14: The Goldilocks Approach

**Slide 35 — The Goldilocks Approach (title)**
- Too little context hurts, too much hurts more

**Slide 36 — Research: "Same Task, More Tokens"**
- Levy, Jacoby, Goldberg (ACL 2024)
- "LLMs' reasoning degrades at much shorter lengths than their technical maximum"
- Effective reasoning ≈ 50-70% of stated max before degradation

**Slide 37 — Mimic the Training Set**
- Use Markdown (that's how models were trained)
- Align with model provider best practices
- XML tags (Anthropic), structured formatting
- Few-shot examples (3-5 is optimal per Google)

**Slide 37b — Anthropic Best Practices (with exact quotes)**

Key principles from Anthropic's official prompt engineering docs (2025):

1. **The Golden Rule:**
   > "Show your prompt to a colleague with minimal context on the task and ask them to follow it. If they'd be confused, Claude will be too."
   — Anthropic, "Be clear and direct"

2. **Long Context Structure (30% improvement):**
   > "Put longform data at the top: Place your long documents and inputs near the top of your prompt, above your query, instructions, and examples. Queries at the end can improve response quality by up to 30% in tests, especially with complex, multi-document inputs."
   — Anthropic, "Long context prompting"

3. **XML Tags for Structure:**
   > "XML tags help Claude parse complex prompts unambiguously, especially when your prompt mixes instructions, context, examples, and variable inputs. Wrapping each type of content in its own tag (e.g. `<instructions>`, `<context>`, `<input>`) reduces misinterpretation."
   — Anthropic, "Use examples effectively"

4. **Ground in Quotes:**
   > "For long document tasks, ask Claude to quote relevant parts of the documents first before carrying out its task. This helps Claude cut through the noise."
   — Anthropic, "Long context prompting"

5. **Give Context/Motivation:**
   > "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals and deliver more targeted responses. Claude is smart enough to generalize from the explanation."
   — Anthropic, "Add context to improve performance"

6. **Persona/Role Assignment:**
   > "Setting a role in the system prompt focuses Claude's behavior and tone for your use case. Even a single sentence makes a difference."
   — Anthropic, "Give Claude a role"

7. **Literal Instruction Following (Opus 4.7):**
   > "Claude Opus 4.7 interprets prompts more literally and explicitly than Claude Opus 4.6. It will not silently generalize an instruction from one item to another, and it will not infer requests you didn't make."
   — Anthropic, "More literal instruction following"

8. **Effort Levels for Agentic Work:**
   > "Start with the new xhigh effort level for coding and agentic use cases, and use a minimum of high effort for most intelligence-sensitive use cases."
   — Anthropic, "Calibrating effort and thinking depth"

**Slide 37c — Research Quotes: Context & Reasoning**

1. **Lost in the Middle (Liu et al., 2023 — TACL):**
   > "Performance is highest when relevant information appears at the very beginning or very end of the context. It degrades significantly — forming a characteristic U-shaped curve — when relevant information is buried in the middle."
   — arxiv.org/abs/2307.03172

2. **Same Task, More Tokens (Levy et al., ACL 2024):**
   > "Our findings show a notable degradation in LLMs' reasoning performance at much shorter input lengths than their technical maximum."
   — arxiv.org/abs/2402.14848

3. **Chain-of-Thought (Wei et al., NeurIPS 2022):**
   > Adding "Let's think step by step" improved MultiArith accuracy from **17.7% to 78.7%** — a 4-word phrase creating a 4.5× improvement.
   — arxiv.org/abs/2201.11903

4. **Zero-Shot Reasoners (Kojima et al., NeurIPS 2022):**
   > "LLMs are decent zero-shot reasoners by simply adding 'Let's think step by step' before each answer."
   — arxiv.org/abs/2205.11916

5. **Google Gemini Docs:**
   > "We recommend to always include few-shot examples in your prompts. Prompts without few-shot examples are likely to be less effective."
   — ai.google.dev/gemini-api/docs/prompting-strategies

---

### Section 14b: Using Different Models — Diversity of Thought

**Slide 37d — Using Different Models (title)**
- "Cognitive diversity > single-model reasoning"
- Same concept as hiring different experts — use different models for different stages

**Slide 37e — The Research: Multi-Model Debate**

Key finding (2024):
> A diverse set of three medium-sized models in debate reached **91% accuracy** on GSM-8K, outperforming GPT-4 and same-model debates (82%).
— "Diversity of Thought Elicits Stronger Reasoning Capabilities in Multi-Agent Debate Frameworks" (2024)

More results:
- **ASDiv benchmark:** Diverse multi-model debate → 94% (new SOTA)
- **MALT** (Multi-Agent LLM Training): generator + verifier + refiner roles → 7-14% relative accuracy gains (Llama 3.1 8B)
- **"Encouraging Divergent Thinking"** (EMNLP 2024): Multi-agent debate avoids "Degeneration-of-Thought" where single models plateau in overconfidence
- **iMAD** (AAAI 2026): Intelligent debate triggering → 92% token reduction, 13.5% accuracy improvement

**Slide 37f — Why Different Models Help**
- Models trained on different data have different blind spots
- Same-model debates collapse to majority opinion (shared misconceptions)
- Different architectures surface different perspectives
- Like having a team of experts who went to different schools

**Slide 37g — Practical Application: The Ralph Loop + SDLC**
- Plan with one model (e.g., Opus for deep reasoning)
- Review with a different model (different blind spots)
- Build with the best coder (e.g., Sonnet for speed)
- Debug with yet another (fresh perspective)
- The `PROMPT_build.md` already does this:
  > "Use Opus subagents when complex reasoning is needed (debugging, architectural decisions)"
  > "Use up to 50 parallel Sonnet subagents for searches/reads"
- Different models at different stages = built-in cognitive diversity

| Stage | Model Choice | Why |
|-------|-------------|-----|
| Planning | Opus (deep reasoning) | Complex analysis, architectural decisions |
| Code search | Sonnet (fast, parallel) | Speed for 500 parallel searches |
| Building | Sonnet/Opus hybrid | Fast iteration + complex problem solving |
| Review | Different provider entirely | Different training data = different blind spots |
| Spec validation | Opus 4.5 "ultrathink" | Catch inconsistencies humans miss |

---

**Slide 38 — The Ralph Loop: Bash-Driven Agent Cycling**
- Show `loop.sh` — a bash script that prompts the agent in a cycle
- Each iteration: fresh `copilot` invocation → clean context window every step
- Captures output, checks for a "completion promise" (`DONE`), pushes git after each loop

**Slide 39 — How It Works (code walkthrough)**
- Code snippet showing the core loop:
  ```bash
  OUTPUT=$(copilot \
      --allow-all-tools \
      --model claude-opus-4.6 \
      -p "$PROMPT_CONTENT" 2>&1 | tee /dev/stderr)

  git push origin "$CURRENT_BRANCH"

  # Check for completion promise
  if echo "$OUTPUT" | grep -q "$COMPLETION_PROMISE"; then
      echo "✓ Completion promise found"
      break
  fi
  ```
- Key: `-p` flag feeds the prompt, `--allow-all-tools` gives full environment access

**Slide 40 — Two Modes: Plan vs Build**
- `./loop.sh -m plan` — runs `PROMPT_plan.md` (research only, no implementation)
- `./loop.sh -m build` — runs `PROMPT_build.md` (implement, test, commit, push)
- Custom: `./loop.sh -p custom_prompt.md -n 3`

**Slide 41 — The Build Prompt (PROMPT_build.md)**
- Show key elements:
  1. Study specs with 500 parallel sub-agents
  2. Implement per specs, search before assuming
  3. Run tests after each unit of work
  4. Update IMPLEMENTATION_PLAN.md with findings
  5. `git commit` + `git push` after passing tests
  6. Output `<promise>DONE</promise>` when complete
- "Completion promise" = deterministic stop signal from non-deterministic agent

**Slide 42 — Why This Uses Every Best Practice**

| Practice | How the Ralph Loop Uses It |
|----------|---------------------------|
| **Clean context window** | Fresh `copilot` invocation each loop — no stale middle context, avoids Valley of Meh |
| **Deterministic hooks** | `git push` after every iteration, tests run every cycle |
| **Validation tools** | Tests, lints, typecheck are required before commit |
| **Skills** | `/git-commit` for structured commits, `/python-code-simplifier` for cleanup |
| **Agents** | Plan agent researches, build agent implements — different expertise per mode |
| **Completion guarantee** | Completion promise (`DONE`) + max iterations = always terminates |
| **Goldilocks context** | Prompt file is compact (~20 lines), specs loaded fresh each time |
| **Structured prompts** | Numbered priorities, clear instructions, Markdown formatting |
| **Mixing determinism** | Bash script (deterministic) wraps AI (non-deterministic) |
| **Environment abilities** | `--allow-all-tools` gives full CLI access inside each iteration |
| **The SDLC cycle** | Plan → Build → Test → Commit → Push → Repeat |

**Slide 43 — The Elegant Insight**
- "Clear the context window, re-anchor every step"
- The agent reads from persistent files (specs, IMPLEMENTATION_PLAN.md, AGENTS.md)
- But starts each iteration with a fresh mind — no accumulated confusion
- Git commits + notes = persistent memory across loops
- IMPLEMENTATION_PLAN.md = the agent's "todo list" that persists across context resets
- Like a developer who writes detailed notes before going to sleep, then picks up fresh the next morning

---

### Section 16: The Agentic SDLC Approach

**Slide 44 — My Agentic SDLC Approach**
- Numbered list:
  1. Plan
  2. Review plan
  3. Review plan again (different agent)
  4. Create Implementation Plan
  5. Build
  6. Test
  7. Debug
  8. Simplify
  9. Refactor
  10. Review
  11. Etc...

**Slide 45 — Key Principle**
- Multiple agents with different expertise review the same work
- Each step feeds into the next
- Deterministic validation (tests, lints) between non-deterministic steps

---

### Section 17: Closing

**Slide 46 — Thank You / Questions**

---

## Technical Implementation Notes

### D3 Visualization (Slide 13)
- Use pre-computed 2D coordinates (no runtime dimensionality reduction)
- D3 v7 via CDN (`cdn.jsdelivr.net/npm/d3@7`)
- 4 personas: Security Engineer (red), Developer (blue), Product Manager (green), Educator (purple)
- 13 concept points that reanimate to different positions per persona
- Convex hulls with `d3-polygon` for cluster boundaries
- Tooltips on hover with concept name + cluster
- Dark background matching Dracula theme
- Buttons trigger `switchPersona()` with 800ms d3-transition animations

### Code Examples to Show
1. Agent file: `.github/agents/plan-agent.md` (frontmatter + first section)
2. Skill file: `.github/skills/git-commit/SKILL.md` (frontmatter + workflow section)
3. Skill with deterministic code: python-code-simplifier showing lint/mypy/test commands

### Reveal.js Configuration
- Theme: Dracula (already configured)
- Plugins: Highlight, Notes, Markdown (already configured)
- Add: `data-background` for section dividers
- Vertical slides (`<section>` nesting) for sub-topics within sections

### Research Citations to Include
- "Lost in the Middle" — Liu et al., 2023, TACL — arxiv.org/abs/2307.03172
- "Same Task, More Tokens" — Levy et al., ACL 2024 — arxiv.org/abs/2402.14848
- "Role-Play Prompting" — Kong et al., NAACL 2024 — arxiv.org/abs/2308.07702
- "Representation Engineering" — Zou et al., 2023 — arxiv.org/abs/2310.01405
- "Scaling Monosemanticity" — Anthropic, May 2024 — transformer-circuits.pub
- "Contrastive Activation Addition" — Panickssery et al., 2023 — arxiv.org/abs/2312.06681
- "SRPS" — Wang et al., EMNLP 2025 — arxiv.org/abs/2506.07335
- Anthropic Prompt Engineering Best Practices — docs.anthropic.com
