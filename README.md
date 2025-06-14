# AI_Agents

A collection of AI agent experiments and projects.

## Setup

This project uses [`uv`](https://github.com/astral-sh/uv) for Python dependency management.

### 1. Install `uv`

```sh
pip install uv
```

Or follow the instructions on the [uv GitHub page](https://github.com/astral-sh/uv).

### 2. Install dependencies

```sh
uv pip install -r simple_agent/uv.lock
```

### 3. Run the main script

```sh
cd simple_agent
python main.py
```

## Notes

- Do **not** commit secrets or API keys to the repository.
- The `.env` file is ignored and should be created locally for environment variables.

## Project Structure

```
AI_Agents/
├── LICENSE
├── README.md
└── simple_agent/
    ├── .gitignore
    ├── .python-version
    ├── README.md
    ├── main.py
    ├── pyproject.toml
    └── uv.lock
```