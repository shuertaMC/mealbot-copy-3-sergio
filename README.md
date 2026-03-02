# Mealbot

A meal pairing service that helps organizations manage member pairings for meals, coffee chats, or similar social interactions. Originally built in Go, now migrated to Python with FastAPI.

## Tech Stack

- **Python 3.11** with type hints
- **FastAPI** web framework
- **SQLAlchemy 2.x** ORM with PostgreSQL
- **Pydantic** for data validation and settings management
- **Uvicorn** ASGI server

## Prerequisites

- Python 3.11+
- PostgreSQL database
- pip (or uv/poetry for dependency management)

## Quick Start

### 1. Install dependencies

```bash
pip install -e ".[dev]"
```

### 2. Configure environment

Copy the example environment file and fill in your local values:

```bash
cp .env.example .env
```

Edit `.env` with your database connection string and other settings:

```
DATABASE_URL=postgresql://user:password@localhost:5432/mealbot
PORT=8080
```

### 3. Run the application

```bash
PYTHONPATH=src uvicorn mealbot_api.main:app --reload
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive API documentation.

### 4. Run tests

```bash
PYTHONPATH=src pytest src/tests/ -v
```

## Docker

### Build the image

```bash
docker build -t mealbot-python .
```

### Run the container

```bash
docker run --env-file .env -p 8080:8080 mealbot-python
```

## API Endpoints

### Organizations (Milestone 1)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/orgs?admin=<email>` | List organizations by admin |
| POST | `/org?admin=<email>` | Create a new organization |
| POST | `/crossmatchtrait?org=<name>` | Set cross-match trait for an org |

### Static Files

| Path | Description |
|------|-------------|
| `/privacy.html` | Privacy policy page |
| `/sample.csv` | Sample CSV template for member import |

## Project Structure

```
src/
  mealbot_api/          # FastAPI app, routes, and API schemas
    main.py             # App factory and ASGI entrypoint
    routes/             # Endpoint definitions
    schemas/            # Pydantic request/response models
    utils.py            # Query parameter helpers
  core/                 # Business logic and domain services
    organizations.py    # Organization CRUD operations
  infra/                # Infrastructure: DB, config, logging
    config.py           # Pydantic settings
    db.py               # SQLAlchemy engine/session
    models.py           # ORM models
    logging.py          # Structured JSON logging
  tests/                # Test suite
static/                 # Static files (privacy.html, sample.csv)
```

## CLI Commands

The application supports CLI subcommands:

```bash
# Run the pairing scheduler (stub - to be implemented)
python -m mealbot_api.main pair

# Run database migration (stub - to be implemented)
python -m mealbot_api.main migrate
```
