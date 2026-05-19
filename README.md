# URL Shortener API

A URL shortener backend built with FastAPI.

## Stack

- **FastAPI** — async web framework
- **PostgreSQL** + **asyncpg** — async database
- **SQLModel / SQLAlchemy** — ORM and async sessions
- **Alembic** — database migrations
- **Redis** — URL redirect cache, JWT blocklist, rate limiting
- **JWT** — stateless authentication with access + refresh tokens

## Features

- Shorten URLs with randomly generated 6-character codes
- Redirect via `GET /{short_code}` with access count tracking
- Redis caching on redirect path
- User accounts with JWT auth (register, login, logout, token refresh)
- Users can create, update, delete, and view stats on their own URLs
- Rate limiting on `POST /shorten` and `POST /login`

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/signup` | Register a new user |
| `POST` | `/api/v1/login` | Login, returns access + refresh tokens |
| `GET` | `/api/v1/refresh_token` | Get a new access token |
| `GET` | `/api/v1/logout` | Revoke current token |

### URLs
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/shorten` | ✅ | Create a short URL |
| `GET` | `/api/v1/shorten/{short_code}` | ✅ | Get URL details |
| `PATCH` | `/api/v1/shorten/{short_code}` | ✅ | Update original URL |
| `DELETE` | `/api/v1/shorten/{short_code}` | ✅ | Delete a short URL |
| `GET` | `/api/v1/shorten/{short_code}/stats` | ✅ | View access count |
| `GET` | `/{short_code}` | ❌ | Redirect to original URL |
| `GET` | `/health` | ❌ | Health check |

## Running Locally

### Prerequisites
- Python 3.12+
- PostgreSQL
- Redis

### Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd url

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env
# Edit .env with your database and Redis connection details

# 5. Run database migrations
alembic upgrade head

# 6. Start the server
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

## Environment Variables

See [`.env.example`](.env.example) for the full list. Key variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (asyncpg driver) |
| `BASE_URL` | Public base URL for generating short links |
| `JWT_SECRET` | Secret key for signing JWTs |
| `REDIS_HOST` | Redis hostname |
| `RATE_LIMIT_MAX` | Max requests per window (default: 10) |
| `RATE_LIMIT_WINDOW` | Window size in seconds (default: 60) |

## Running Tests

```bash
pytest
# With coverage
pytest --cov=src
```

## Deployment

This app is configured to deploy on **Render** using Docker.

See [`docker.md`](docker.md) for full instructions including:
- Running with Docker Compose locally
- Step-by-step Render deployment guide
- How migrations are handled at deploy time
