# Morning Signal

Morning Signal is an autonomous, personal **QA-only** digest focused on QA automation, Agentic QA, AI for QA, software testing, test reliability, and modern quality engineering practices. It creates a small structured JSON edition each morning, validates it, renders static HTML, archives it, and publishes it with GitHub Pages.

Generic AI, coding-agent, software-development, cloud, platform, company, and technology news is intentionally excluded unless it has a clear and substantial impact on software testing or quality engineering.

The checked-in `2026-08-18` issue is an explicitly labeled bootstrap fixture. It is there to make the first deployment useful and testable; it is not presented as live news.

## Architecture

```text
GitHub Actions schedule (07:35 Europe/Warsaw)
        |
        v
RSS / release feeds ---> normalized candidates
        |                         |
        +----> OpenAI Responses API + bounded QA-focused web search
                                      |
                                      v
                         strict structured digest JSON
                                      |
                         validate / deduplicate / rank
                                      |
                         deterministic Jinja2 HTML/CSS
                                      |
                          archive + static homepage
                                      |
                         commit --> GitHub Pages
```

The site is static. The browser never calls OpenAI and no API key is included in frontend assets.

## Editorial scope

Morning Signal publishes only items with direct QA/testing relevance. The primary areas are:

- QA automation and quality engineering
- Agentic QA and QA agents
- AI-assisted testing and AI for QA
- testing/evaluation of AI-powered software
- mobile QA: Appium, Espresso, XCUITest, Maestro, device farms and SDK testing
- web/API automation: Playwright, Cypress, Selenium, Pytest and related testing tools
- flaky-test investigation, test reliability, test observability and test infrastructure
- performance, load and stress testing
- CI quality gates and release quality when directly connected to QA
- QA-focused releases, documentation, research, talks and engineering practices

Adjacent technology news is ignored unless it materially changes how software is tested, validated or released.

## Local setup

Python 3.9+ is supported. Create an environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` only for local use and export the values in your shell. `.env` is ignored by Git.

## OpenAI API configuration

Live generation needs `OPENAI_API_KEY`. The model is configurable with `OPENAI_MODEL` and defaults to `gpt-5-mini`. The pipeline uses the OpenAI Responses API with the hosted `web_search` tool and structured JSON Schema output. `store=False` is set for the response request.

```bash
set -a; source .env; set +a
export OPENAI_API_KEY='your-key'
export OPENAI_MODEL='gpt-5-mini'
export MAX_OUTPUT_TOKENS=30000
export MAX_WEB_SEARCHES=6
export MIN_DIGEST_ITEMS=20
export MAX_DIGEST_ITEMS=25
```

The current official API pattern is documented in the [OpenAI developer quickstart](https://platform.openai.com/docs/quickstart/make-your-first-api-request) and the [Responses API reference](https://platform.openai.com/docs/api-reference/responses).

## Generate a digest manually

```bash
python scripts/generate_digest.py
python scripts/render.py
```

`generate_digest.py` validates the JSON before atomically writing `data/YYYY-MM-DD.json`. `render.py` stages the entire static site and promotes it only after successful rendering. Use `--date YYYY-MM-DD` when you need a specific issue date.

For an offline preview, render the checked-in fixture:

```bash
python scripts/render.py
```

## Tests and preview

```bash
python -m pytest
python scripts/validate.py
python -m http.server 8000
```

Open <http://localhost:8000>. `make test`, `make generate`, `make render`, `make validate`, and `make serve` are convenient aliases.

## GitHub Actions

`.github/workflows/morning-digest.yml` runs once daily and also supports `workflow_dispatch`. The job installs dependencies, runs tests, generates and validates JSON, renders the site, runs the final tests, and commits only intended generated files.

`.github/workflows/pages.yml` deploys the repository contents using the official GitHub Pages artifact/deploy actions.

## GitHub Secrets and Pages

Add the repository secret `OPENAI_API_KEY` under Settings → Secrets and variables → Actions. Optionally add the repository variable `OPENAI_MODEL`.

To enable Pages, open Settings → Pages, choose **GitHub Actions** as the source, and let the Pages workflow deploy the `main` branch. The workflow has the minimum `pages: write`, `id-token: write`, and `contents: read` permissions it needs.

## Cost controls

The pipeline is RSS-first and sends a compact candidate list to one editorial call. It defaults to a 30,000-token response budget, at most six focused web searches (instructed at the API boundary), at least twenty and at most twenty-five total stories, 40 candidates, and a 72-hour lookback. These values can be changed with `MAX_OUTPUT_TOKENS`, `MAX_WEB_SEARCHES`, `MIN_DIGEST_ITEMS`, `MAX_DIGEST_ITEMS`, `MAX_CANDIDATES`, and `LOOKBACK_HOURS`. Editions below the minimum are rejected before publication. There are no multi-agent loops or database calls.

## Archive design

Each successful issue creates `data/YYYY-MM-DD.json` and `archive/YYYY-MM-DD.html`. The newest issue is rendered to `index.html`, while `archive/index.html` is regenerated in reverse chronological order. Historical pages contain all content and source links statically; they do not depend on an API call.

## Personalization and sources

Edit `config/interests.yaml` to change QA ranking guidance. Edit `config/sources.yaml` to add a primary RSS/Atom feed with a category and quality score. Broad engineering feeds may remain as discovery inputs, but their articles are ignored by the editorial stage unless they have direct QA/testing relevance. Collection failures are logged as warnings and do not erase an existing site; a run that cannot produce a valid digest fails before promotion.

## Troubleshooting

- `OPENAI_API_KEY is required`: export the key or configure the GitHub Actions secret.
- `No digest JSON files found`: keep the bootstrap fixture or generate a live issue before rendering.
- Feed warnings: a source may be temporarily unavailable; other sources can still be collected.
- A failed generation leaves the previous `index.html` in place because publishing happens only after staged validation.
- If Pages is not deploying, confirm the repository Pages source is set to **GitHub Actions** and inspect the Pages workflow permissions.

## License

MIT. See [LICENSE](LICENSE).
