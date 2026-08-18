# Morning Signal — autonomous QA / Agentic AI morning digest

You are a senior software engineer, QA automation engineer, AI agent engineer, and DevOps engineer.

Your task is to design, build, test, verify, and publish a complete production-ready project called `morning-signal`.

Do NOT immediately start coding.

Follow the execution phases below strictly.

---

# 0. GOAL

Build an autonomous personal morning technology digest focused on:

* QA Automation
* Agentic Engineering
* AI Agents
* AI/LLM testing
* LLM evals
* RAG evaluation
* Mobile QA
* Android
* Maestro
* Espresso
* SDK testing
* Python / Pytest
* TypeScript / Playwright
* GitHub Actions
* CI/CD
* test infrastructure
* observability
* flaky test investigation
* device farms
* BrowserStack
* engineering practices
* relevant engineering blogs
* new tools/frameworks
* important releases
* documentation drops
* useful conference talks/webinars
* important company engineering insights

The system should autonomously create a curated morning digest every day and publish it as a beautiful static website.

Project name:

`morning-signal`

Preferred GitHub repository:

`morning-signal`

The site should be deployable for free using GitHub Pages.

---

# 1. IMPORTANT ARCHITECTURAL PRINCIPLES

Use a simple deterministic pipeline.

Do NOT build an unnecessarily complex autonomous multi-agent system.

Do NOT use MCP in v1 unless there is a clear technical reason.

Architecture:

```text
GitHub Actions schedule
        ↓
Source collection
        ↓
OpenAI Responses API + web search
        ↓
Structured JSON digest
        ↓
Validation / deduplication
        ↓
Deterministic HTML rendering
        ↓
Archive generation
        ↓
Git commit
        ↓
GitHub Pages deployment
```

The website itself must NOT call OpenAI.

The website must be static.

Never expose the OpenAI API key in frontend code.

The AI should generate structured data, not arbitrary HTML.

HTML must always be generated deterministically from templates.

---

# 2. EXECUTION PHASES

You MUST execute the project in the following order.

## PHASE 1 — ANALYSIS AND PLAN

Before writing code:

1. Inspect the current working directory.
2. Inspect existing files.
3. Inspect Git status if this is already a repository.
4. Look for an existing reference HTML design, especially a file similar to:

`qa_agentic_ai_morning_digest.html`

5. Inspect available environment/tooling.
6. Check whether GitHub CLI `gh` is installed and authenticated.
7. Identify Python version.
8. Identify any constraints of the current environment.

Then create a concise implementation plan containing:

* architecture
* file structure
* data flow
* OpenAI integration
* source collection strategy
* archive strategy
* GitHub Actions strategy
* GitHub Pages deployment strategy
* test strategy
* security considerations
* API cost controls
* failure handling

DO NOT begin implementation until the plan is complete.

You do not need to wait for human confirmation unless there is a truly blocking issue.

## PHASE 2 — IMPLEMENTATION

Prefer a simple structure close to:

```text
morning-signal/
├── index.html
├── archive/
├── data/
├── assets/style.css
├── templates/
├── scripts/
├── config/
├── tests/
├── .github/workflows/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE
```

Create configurable personal relevance in `config/interests.yaml`, including high-priority QA automation, agentic engineering, AI agents, AI testing, LLM evals, mobile QA, Android, Maestro, Espresso, SDK testing, Python, Pytest, Playwright, GitHub Actions, CI/CD, and test infrastructure interests; medium-priority RAG, observability, AdTech, BrowserStack, device farms, flaky-test investigation, engineering management, and release engineering; career focus on senior QA automation, QA lead/manager, mobile automation, agentic QA, and AI QA engineering; and low-priority generic consumer AI, funding, cryptocurrency, celebrity AI, and gadget news.

Create `config/sources.yaml` with high-quality primary RSS/Atom/API sources such as OpenAI, Anthropic, GitHub, Android Developers, Maestro, Playwright, BrowserStack, JetBrains, Microsoft engineering blogs, relevant engineering company blogs, GitHub releases, conference/event pages, and important research sources. Avoid dozens of random SEO aggregators.

Implement a hybrid research pipeline:

1. Collect recent candidates from configured feeds, approximately 24–72 hours old, without downloading huge amounts of content.
2. Normalize candidates with title, URL, source, published date, category, and summary.
3. Use the current supported official OpenAI Responses API and web search to discover missed developments, confirm claims, locate primary sources, verify dates, and find relevant talks/events/releases.
4. Make the model configurable with `OPENAI_MODEL` and the key supplied by `OPENAI_API_KEY`.
5. Produce strict structured JSON, never HTML.

Keep the pipeline cheap: approximately six web-search operations maximum, ten final stories maximum, RSS/API-first collection, compact prompts, one main ranking/editorial call where practical, and no uncontrolled loops. Expose limits through configuration/environment such as `MAX_WEB_SEARCHES=6` and `MAX_DIGEST_ITEMS=10`.

Validate required fields, URL validity, priority range, duplicate links, duplicate or near-duplicate stories, item count, and ISO date format. Prefer original source URLs. Avoid hype, clickbait, invented facts, generic tech-news noise, and random AI funding news.

Render a premium editorial static site with a light gray background, white surfaces, near-black text, neutral muted text, restrained blue accent, generous whitespace, large typography, rounded cards, subtle borders/shadows, responsive layout, and minimal JavaScript. Include the Morning Signal header, date, hero, interest chips, Top Signal, What Moved, priority score, Why it matters, source links, Watch, Worth Learning Today, and archive navigation. Test desktop, tablet, and mobile behavior and avoid horizontal scrolling or overflow.

Every successful daily run must create `data/YYYY-MM-DD.json`, `archive/YYYY-MM-DD.html`, regenerate `archive/index.html` newest first, and make the newest edition `index.html`. Historical pages must be static and independent of APIs.

If no approved sample exists, provide a clearly labeled bootstrap/sample fixture for `2026-08-18` without presenting fabricated current news as real.

Create scheduled and manually triggerable GitHub Actions. The schedule should target approximately 07:35 Europe/Warsaw, usually before 08:00. The workflow must check out, install Python dependencies, run tests, generate, validate, render, run final tests, and commit/push only after success. Do not commit invalid JSON, broken HTML, empty digests, or secrets. Use minimal permissions. Add a current official GitHub Pages workflow/action and explain manual Pages enablement in the README if needed.

Use only `OPENAI_API_KEY` as a GitHub Actions secret. Ignore `.env`, never print secrets, and scan the repository before pushing.

Temporary API/feed failure must not destroy the existing website. Stage and validate generated files first; leave the previous homepage intact on failure and fail the Action with useful non-secret diagnostics.

Write meaningful tests covering JSON validation, invalid priorities/URLs, duplicate links, item limits, HTML title/date/source/Top Signal rendering, archive ordering and links, and failure safety when an invalid digest is rendered.

Provide local commands such as:

```bash
python -m pytest
python scripts/generate_digest.py
python scripts/render.py
python -m http.server 8000
```

Create a complete README explaining the project, architecture, local setup, OpenAI configuration, manual generation, tests, local preview, GitHub Actions, secrets, Pages, cost controls, archive design, troubleshooting, interests, and source configuration.

## PHASE 3 — AUTOMATED VERIFICATION

Run unit and integration-level rendering tests, Python syntax checks, generated JSON validation, HTML generation, archive generation, broken internal-link checks, configuration parsing, duplicate detection, secret scanning, and Git diff inspection. Fix failures and rerun relevant tests.

## PHASE 4 — REQUIREMENTS AUDIT

Reread this entire specification and audit every major requirement against the actual files. Explicitly verify autonomous generation, archive, static site, no frontend key, OpenAI usage, cost control, primary sources, deterministic templates, JSON validation, deduplication, scheduled/manual Actions, failure safety, Pages, responsive design, tests, documentation, and secrets. Fix gaps.

## PHASE 5 — DESIGN AUDIT

Open/render the generated homepage, archive, and archived issue locally at desktop and mobile sizes where tooling permits. Inspect spacing, typography, card hierarchy, colors, priority labels, Top Signal prominence, Watch, Worth Learning, source links, archive, mobile layout, overflow, and unstyled/generic dashboard problems. Fix visual issues.

## PHASE 6 — FINAL PRE-COMMIT REVIEW

Run the complete test suite one final time, then inspect `git status` and `git diff`. Verify there is no API key, `.env`, temporary/debug file, unnecessary generated garbage, credential, or broken path. Confirm only intended project changes remain.

## PHASE 7 — GIT AND GITHUB

Only after all previous phases pass:

1. Initialize Git if necessary.
2. Ensure default branch is `main`.
3. Create a sensible `.gitignore`.
4. Stage only intended files.
5. Commit with a clear message such as `feat: build autonomous Morning Signal digest`.
6. If `gh` is authenticated, create or inspect the preferred public `morning-signal` repository, add the remote, and push `main` without force-pushing or overwriting unrelated work.

## PHASE 8 — GITHUB CONFIGURATION

After pushing, verify the remote repository and workflow files, configure Pages if possible, and configure `OPENAI_API_KEY` as a GitHub Actions secret only if safe and appropriate. Otherwise clearly state the exact manual secret step without printing the secret.

## PHASE 9 — REMOTE TEST

After push, inspect Actions, trigger the workflow manually where possible, monitor the result, fix failures, push fixes, and rerun until it passes or a genuine external blocker such as missing credentials is reached.

## PHASE 10 — DEPLOYMENT TEST

After Pages deployment, verify HTTP success, homepage, CSS, archive, archived digest, links, and responsive layout where network/browser tooling permits. Investigate and fix deployment problems.

## ACCEPTANCE CRITERIA

The project is complete only when feasible criteria are satisfied: repository exists; clean structure; tests pass; static homepage works; approved light design is preserved; mobile layout works; archive works; first digest exists; structured JSON is stored; OpenAI research integration exists; current official API syntax is verified; the key is secret; cost controls exist; scheduled generation targets approximately 07:35 Europe/Warsaw; manual trigger exists; failed generation cannot destroy the existing site; Pages configuration exists; README is complete; requirements and design audits are complete; final local tests pass; code is committed and pushed; remote Actions are tested where credentials allow; and the deployed site is tested where tooling allows.

Do not cut corners or declare success after only generating files. Do not commit or push before verification. Do not redesign the approved site into a generic developer dashboard. Do not use AI-generated HTML for daily editions. Do not expose secrets. Do not introduce unnecessary infrastructure or a database. Prefer Python + Jinja2 + static HTML/CSS + GitHub Actions + GitHub Pages. Keep v1 boring, transparent, cheap, and reliable.

## FINAL REPORT

When finished, report architecture, tests and results, requirements-audit deviations/compromises, GitHub repository and branch, deployment URL, automation schedule/manual trigger, secrets requiring manual configuration, cost controls, and no more than five useful v2 ideas. If externally blocked, state exactly what is blocked, what is complete, and the exact manual step needed.
