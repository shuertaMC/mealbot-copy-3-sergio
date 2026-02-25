# Mealbot

A meal-pairing application migrated from Go to Python (Flask).

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and populate with real values.

### Database Setup

Create a PostgreSQL database and run `schema.sql`:

```bash
psql -d mealbot -f schema.sql
```

### Running the Application

```bash
export FLASK_APP=mealbot.app:create_app
flask run --port=${PORT:-5000}
```

### Running Tests

```bash
pytest
```

## Deployment

Configured for Heroku via `Procfile` using gunicorn.
