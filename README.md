# AI_Agents

A collection of AI agent experiments and projects.

---

## Project Structure

```
AI_Agents/
├── LICENSE
├── README.md
├── multi_agent/
│   ├── .gitignore
│   ├── .python-version
│   ├── README.md
│   ├── main.py
│   ├── pyproject.toml
│   └── uv.lock
└── simple_agent/
    ├── .gitignore
    ├── .python-version
    ├── README.md
    ├── main.py
    ├── pyproject.toml
    └── uv.lock
```

---

## Getting Started

This project uses [`uv`](https://github.com/astral-sh/uv) for Python dependency management.

### 1. Install `uv`

```sh
pip install uv
```
Or see [uv installation instructions](https://github.com/astral-sh/uv).

### 2. Install dependencies

For each agent, install dependencies from its directory:

```sh
cd simple_agent
uv pip install -r uv.lock

cd ../multi_agent
uv pip install -r uv.lock
```

### 3. Run an agent

For example, to run the simple agent:

```sh
cd simple_agent
python main.py
```

Or to run the multi agent:

```sh
cd multi_agent
python main.py
```

---

## Notes

- **Secrets:** Do **not** commit secrets or API keys. Use a local `.env` file for environment variables (already gitignored).
- **Python Version:** Each agent uses the Python version specified in its `.python-version` file.
- **Dependencies:** Managed with `uv` and locked in `uv.lock` for each agent.

---

## More Information

See the `README.md` files inside `simple_agent/` and `multi_agent/` for agent-specific documentation.

---

## License

See [LICENSE](LICENSE) for details.
