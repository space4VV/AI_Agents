# AI_Agents

A collection of AI agent experiments and projects.

---

## Project Structure

```
AI_Agents/
├── LICENSE
├── README.md
├── .flake8
├── .pre-commit-config.yaml
├── advanced_agent/
│   ├── .env
│   ├── .python-version
│   ├── advanced_agent.py
│   ├── pyproject.toml
│   ├── uv.lock
│   └── src/
│       ├── __init__.py
│       ├── firecrawl.py
│       ├── models.py
│       ├── prompts.py
│       └── workflow.py
├── simple_agent/
│   ├── .env
│   ├── .gitignore
│   ├── .python-version
│   ├── main.py
│   ├── pyproject.toml
│   └── uv.lock
└── testing.ipynb
```

---

## Getting Started

This project uses [`uv`](https://github.com/astral-sh/uv) for Python dependency management.

### 1. Install `uv`

```sh
pip install uv
```

### 2. Install dependencies

For each agent, install dependencies from its directory:

```sh
cd advanced_agent
uv pip install -r uv.lock

cd ../simple_agent
uv pip install -r uv.lock
```

### 3. Run an agent

For example, to run the advanced agent:

```sh
cd advanced_agent
python advanced_agent.py
```

Or to run the simple agent:

```sh
cd simple_agent
python main.py
```

---

## Notes

- **Secrets:** Do **not** commit secrets or API keys. Use a local `.env` file for environment variables (already gitignored).
- **Python Version:** Each agent uses the Python version specified in its `.python-version` file.
- **Dependencies:** Managed with `uv` and locked in `uv.lock` for each agent.
- **Linting:** Uses `flake8` with a line length of 120 (see `.flake8`).
- **Pre-commit:** Uses pre-commit hooks as configured in `.pre-commit-config.yaml`.

---

## License

See [LICENSE](LICENSE) for details.
