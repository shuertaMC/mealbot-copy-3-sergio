# Mealbot

A meal pairing application that helps organizations create random pairings among their members for meals and social events.

## Get Started

### Prerequisites
- Python 3.12+
- PostgreSQL

### Database
- Download Postgres [here](https://www.postgresql.org/download/)
- Create a Postgres database
- Set up the database schema by executing `schema.sql`

### Python Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Configuration
- Copy `.env.example` to `.env` and fill in your values
- Key environment variables:
  - `DATABASE_URL` - PostgreSQL connection string
  - `PORT` - Server port (default: 5000)
  - `AUTH0_ISSUER`, `AUTH0_AUDIENCE`, `AUTH0_JWKS_URL` - Auth0 configuration
  - `MAILGUN_SMTP_LOGIN`, `MAILGUN_DOMAIN`, `MAILGUN_API_KEY` - Mailgun configuration

### Running the Application
```bash
# Development
export FLASK_APP=mealbot.app:create_app
flask run --port=${PORT:-5000}

# Production (Heroku)
# Uses Procfile: gunicorn "mealbot.app:create_app()"
```

### CLI Commands
```bash
flask pair     # Run pairing rounds
flask migrate  # Run data migrations
```

### Running Tests
```bash
pytest
```

## Miscellanea
- Originally built in Go, now migrated to Python with Flask
- Package management handled via `requirements.txt`
