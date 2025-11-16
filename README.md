# Elders Helping Backend

Comprehensive Django 4.x REST API backend for the "Elders Helping App" — built with Django REST Framework, PostgreSQL, Redis/Celery, JWT auth and ready for Docker / Render (Docker) deployment.

This repository contains:

- Django project: `elders_helping`
- Two apps: `apps/core` (models, API, tasks) and `apps/users` (OTP auth, profiles)
- Celery configuration and example tasks (`apps/core/tasks.py`)
- Docker and `docker-compose.yml` for local development
- OpenAPI schema + Swagger UI via `drf-spectacular` at `/api/schema/` and `/api/docs/`
- Seed command: `python manage.py seed_data`

**Important files**:
- `Dockerfile`, `docker-compose.yml`, `.env.example`
- `apps/core/models.py` — data model (based on ER diagram)
- `apps/core/viewsets.py` — core API ViewSets
- `apps/users/views.py` — OTP send/verify + JWT issuance
- `apps/core/views_webhooks.py` — payment webhook handler (simulated)

**Local Quick Start (Docker, recommended)**

1. Clone the repo and change directory:

```
git clone <repo-url> elders-helping-backend
cd elders-helping-backend
```

2. Copy and edit environment variables:

```
cp .env.example .env
# Edit .env according to your environment (DB credentials, SECRET_KEY, FRONTEND_URL...)
```

3. Start services with Docker Compose (use `docker compose` if you have Docker Desktop):

```powershell
docker compose up --build -d
```

4. Run migrations and seed initial data:

```powershell
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_data
```

5. Create an interactive superuser (optional):

```powershell
docker compose exec web python manage.py createsuperuser
```

6. Run tests:

```powershell
docker compose exec web python manage.py test
```

**If you don't use Docker (local Python)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver 0.0.0.0:8000
```

**API docs / Swagger**

- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI Schema (JSON/YAML): `http://localhost:8000/api/schema/`

Use the `Authorize` button in Swagger to add `Authorization: Bearer <access_token>` after you obtain the JWT from the OTP verify endpoint.

**Auth (OTP + JWT) — dev flow**

1) Send OTP (logs OTP to server in dev):

```
curl -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone":"+919876543210"}'
```

Response: `{ "otp_token": "<uuid>" }` and the server console will contain a line like `[DEV OTP] token=<uuid> otp=123456`.

2) Verify OTP and receive JWT tokens:

```
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"otp_token":"<uuid>","otp":"123456","role":"donor"}'
```

Response: `{ "access": "<jwt>", "refresh": "...", "user": {...} }`

Use the `access` token as `Authorization: Bearer <access>` for protected endpoints.

**Key API endpoints**

- `POST /api/auth/send-otp/` — send OTP (dev logs OTP)
- `POST /api/auth/verify-otp/` — verify OTP and issue JWT
- `GET /api/requests/` — public list of care requests
- `POST /api/requests/` — create a care request (auth required)
- `POST /api/donations/` — create a donation (returns simulated payment_intent)
- `POST /api/payments/webhook/` — simulate payment provider webhook

Refer to `docs/API_spec.md` for more details.

**Payments & Webhooks (simulated)**

- The donations endpoint creates `Donation` objects and simulates a `payment_intent` in its response.
- The webhook endpoint `POST /api/payments/webhook/` accepts JSON with `{provider, provider_payment_id, donation_id, status}` and updates `Payment` and `Donation` records, and creates `Notification` objects for donor and NGO.

Example webhook simulation:

```bash
curl -X POST http://localhost:8000/api/payments/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"provider":"razorpay","provider_payment_id":"pay_ABC","donation_id":1,"status":"paid"}'
```

**Celery & Periodic Tasks**

- Celery is configured using Redis (see `CELERY_BROKER_URL` in `settings.py`).
- The project registers example tasks in `apps/core/tasks.py`:
  - `send_medication_reminders`
  - `send_appointment_reminders`
  - `daily_digest`
- `docker-compose.yml` includes `worker` and `beat` services to run Celery worker and beat (database scheduler via `django-celery-beat`).

**Media & Storage**

- Local media is stored in `media/` during `DEBUG=True`.
- For production use S3 or Firebase. Example S3 settings (add to `settings.py` when `DEBUG=False`):

```py
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
# AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
# AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
```

- Firebase: use a community Firebase storage adapter or signed-upload flow. Keep credentials out of the repo and in environment variables.

**Security & Validation**

- OTP endpoints are throttled to mitigate abuse.
- File uploads should be validated for content type and size. Add validation in serializers or upload handlers (allowed image types, size limits).
- Role-based permissions are enforced at viewset level; extend `permissions.py` (in `apps/core`) to implement granular rules (NGO-only endpoints, admin moderation).
- Ensure `SECRET_KEY` is set in environment (don't use `.env.example` in production).

**Environment variables (.env.example explained)**

- `DEBUG` — set to `False` in production.
- `SECRET_KEY` — Django secret key.
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT` — Postgres connection.
- `REDIS_URL` — Redis connection for Celery and cache.
- `SIMPLE_JWT_ACCESS_TOKEN_LIFETIME_MINUTES` — access token lifetime.
- `FRONTEND_URL` — allowed CORS origin for front-end.
- `DJANGO_SUPERUSER_*` — credentials used by seed/script for initial superuser.

**Testing**

- Basic tests included at `apps/core/tests/` and `apps/users/tests/`.
- Run tests locally with `python manage.py test` or inside Docker: `docker compose exec web python manage.py test`.

**Seed data**

- `python manage.py seed_data` creates roles, sample cities, a superuser (from env vars), a sample NGO, volunteer, donor and several sample requests.

**Render (Docker) Deployment Notes**

1. Create a new Web Service on Render and connect your GitHub repo.
2. Use Docker as the environment and set the start command to:

```
gunicorn elders_helping.wsgi:application --bind 0.0.0.0:$PORT --workers=3
```

3. Add environment variables in Render using values from `.env.example` (SECRET_KEY, DB URL, REDIS URL, etc.).
4. Add a managed PostgreSQL and Redis instance in Render and use their connection strings.
5. Add additional services for Celery worker and Celery beat pointing to the same Docker image.

**Commit history / Deliverables**

The repository was scaffolded with commits to reflect the requested milestones. Suggested commit messages (used during development):

- `chore: initial repo scaffold & README`
- `feat: add django project, apps and basic settings`
- `feat(core): add models based on ER diagram and migrations`
- `feat(auth): OTP send/verify and JWT authentication`
- `feat(api): add serializers, viewsets and routers for requests/donations/messages`
- `feat: add celery config and example tasks`
- `chore: add docker, docker-compose and .env.example`
- `test: add basic tests for OTP, requests, donations`
- `docs: add API docs + Render deploy instructions`
- `chore: seed data and scripts`

**Next steps I can help with**

- Run the Docker Compose stack here and report back errors.
- Add fine-grained role permissions and rate limiting rules.
- Integrate real payment provider (Razorpay / Stripe) and add signature verification.
- Hook up S3/Firebase storage and add file validation middleware.

If you want me to perform any of these next steps now, tell me which one and I'll continue.

Storage (Firebase/S3):
- In production you can enable `django-storages` with `boto3` or a Firebase storage adapter.
- Example S3 settings (in `settings.py` when DEBUG=False):

```py
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
# AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
# AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
```

For Firebase, use a community storage adapter or configure uploads to a signed URL flow. Include credentials via environment variables and keep them secret.




http://127.0.0.1:8000/api/docs/#/
For Swagger


