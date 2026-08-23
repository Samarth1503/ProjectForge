# ProjectForge: Local Development & Quick Start Guide

Welcome to ProjectForge! This guide will walk you through setting up the project locally on your machine and demonstrate how to use it to generate your first project blueprint.

---

## 1. Prerequisites

Before you begin, ensure you have the following installed on your system:
* **Python 3.12+**
* **uv** (An extremely fast Python package installer and resolver). If you don't have it, install it via:
  * Windows (PowerShell): `irm https://astral.sh/uv/install.ps1 | iex`
  * macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
* **Google Gemini API Key**: You can get one from Google AI Studio.

---

## 2. Local Environment Setup

1. **Navigate to the project directory** (or clone the repository if you haven't already).
2. **Install dependencies** using `uv`. This will automatically create a virtual environment and install all packages defined in `pyproject.toml`.
   ```bash
   uv sync
   ```

*(Note: Depending on your terminal, you may need to ensure `uv` is in your PATH. If you just installed `uv` on Windows, you might need to restart your PowerShell or run `$env:Path = "$HOME\.local\bin;$env:Path"`).*

---

## 3. Quick Start: Creating a Rock, Paper, Scissors Bot

Let's use ProjectForge to design the architecture, requirements, and database for a Rock, Paper, Scissors Discord bot.

### Step 1: Initialize the Workspace
Run the CLI initialization command. This will scaffold the configuration files in your current directory.
```bash
uv run python -m projectforge init
```
This command generates two files:
* `.env`: Where you will store your API key.
* `project_context.json`: A template file describing the project you want to build.

### Step 2: Configure your API Key
Open the newly created `.env` file and paste your Gemini API key:
```env
GEMINI_API_KEY=AIzaSyYourSecretKeyGoesHere...
```

### Step 3: Define the Project Idea
Open `project_context.json` and replace the placeholder text with the details for our Rock, Paper, Scissors bot. It should look like this:

```json
{
  "project_title": "RPS-Discord-Bot",
  "project_description": "A Discord bot that allows users to play Rock, Paper, Scissors against an AI. The bot should track win/loss statistics and maintain a global server leaderboard.",
  "project_type": "other",
  "tech_preferences": [
    "Python",
    "discord.py",
    "SQLite"
  ],
  "target_users": "Discord server members",
  "constraints": [
    "Must respond in under 2 seconds",
    "Must use Discord Slash Commands"
  ],
  "team_size": 1,
  "timeline_weeks": 2,
  "academic_level": "undergrad",
  "additional_notes": "Keep the database schema simple, one table for user stats is enough."
}
```

### Step 4: Run the AI Pipeline
Now, instruct ProjectForge to analyze your idea and generate the blueprints!

```bash
uv run python -m projectforge run
```

### Step 5: Review Your Blueprints
ProjectForge will automatically execute its internal skills in the correct order (e.g., Requirements -> Architecture -> Database -> API -> Project Plan).

Once the command finishes, check the newly created **`blueprint/`** directory. Inside, you will find detailed JSON files like `requirements.json`, `architecture.json`, and `database.json`, containing structured, ready-to-implement specifications for your bot!

---

## 4. Developer Workflow

If you want to contribute to the ProjectForge codebase itself, here are the essential commands.

### Running Tests
ProjectForge uses `pytest` and heavily utilizes a `FakeAIProvider` so you don't need network access or an API key to run tests locally.

To run the test suite and check code coverage:
```bash
uv run pytest
```

### Modifying the Codebase
* **Core Logic:** Found in `src/projectforge/`
* **Adding a New Skill:** 
  1. Create a new folder under `src/projectforge/skills/`.
  2. Define your Pydantic schemas in `schema.py`.
  3. Create your class in `skill.py` extending `BaseSkill` and decorate it with `@register_skill`.
  4. Import your skill in `src/projectforge/skills/__init__.py`.
* **CLI:** Found in `src/projectforge/cli/main.py`.
