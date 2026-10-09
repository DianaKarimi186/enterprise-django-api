# Deployment guide

## Recommended architecture

The root Dockerfile now builds the React/Vite app and the Django API into one image. Django serves the built frontend at `/`, static assets through WhiteNoise, and API endpoints under `/api/`. Keeping the frontend and API on the same origin avoids a separate CORS configuration.

This setup requires a hosting plan that can build and run the repository's Dockerfile. I have not assumed that the Hostiga account/plan supports Docker; confirm that in the provider dashboard before choosing this deployment path.

## Required production environment

Configure these as host environment variables, not in Git:

- `DJANGO_SECRET_KEY`: a unique, strong secret value
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`: the production hostname, without the scheme; comma-separated if needed
- `DATABASE_URL`: the PostgreSQL connection URL supplied by the database host
- `DJANGO_CSRF_TRUSTED_ORIGINS`: comma-separated HTTPS origins if cross-origin browser form requests are used

`REDIS_URL` is optional for the core dashboard. Without it, Django uses local-memory caching; background Celery work requires a reachable broker and a separately running worker.

Do not commit real passwords, database URLs, secret keys, or production tokens.

## Build and start

The Dockerfile installs frontend and Python dependencies, builds `frontend/dist`, copies it into the Django image, and runs `collectstatic`. The web process starts with Gunicorn and uses the `PORT` environment variable when supplied by the host.

Before serving real traffic, run database migrations as a one-off release/deploy command:

```bash
python manage.py migrate
```

Create an administrator if needed:

```bash
python manage.py createsuperuser
```

If your host does not offer a one-off release command, run migrations through its documented deployment console before directing traffic to the new release. Avoid running migrations concurrently from multiple web instances.

## Validation checklist

1. Confirm the host supports Docker builds and the configured Python/Node runtimes.
2. Configure a persistent PostgreSQL database and set `DATABASE_URL`.
3. Set the environment variables above and confirm HTTPS termination/proxy headers are supported.
4. Deploy and verify `/`, `/api/docs/`, and an authenticated request to `/api/products/dashboard/metrics/`.
5. Confirm the frontend can sign in and create, edit, filter, and delete a test product.
6. Run `python manage.py check --deploy` with production environment values.
7. If Celery tasks are needed, configure Redis and a separate Celery worker process.

The GitHub branch contains configuration and tests, but deployment is not complete until a host is selected, secrets and database are configured, and the live smoke tests pass.
