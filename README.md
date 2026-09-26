# IronLane Freight

Marketing website for a trucking / freight operating company: services, fleet, a quote
request form and a driver-application form. Submissions are validated with Pydantic,
stored in the database (visible in Django admin) and emailed to dispatch.

## Stack

| Layer      | Version                          | Why                                        |
|------------|----------------------------------|--------------------------------------------|
| Python     | 3.13                             | Mature release, supported until Oct 2029   |
| Django     | 5.2 LTS                          | Long-term support until April 2028         |
| Pydantic   | 2.x + pydantic-settings          | Typed env config and form validation       |
| Tailwind   | 4.3 (standalone CLI via npm)     | Utility CSS, built into `output.css`       |
| Serving    | gunicorn + whitenoise + nginx    | Same setup as alano_group                  |
| Tooling    | uv, ruff                         | Dependency management and lint/format      |

Version ranges in `pyproject.toml` are capped at the next major/minor (`django<5.3`,
`pydantic<3`), and `uv.lock` pins the exact versions.

## Local development

```bash
uv sync                       # Python deps (creates .venv)
npm install                   # Tailwind CLI
cp .env.example .env          # then set SECRET_KEY, DEBUG=True

npm run watch:css             # terminal 1: rebuild CSS on change
uv run python source/manage.py migrate
uv run python source/manage.py createsuperuser
uv run python source/manage.py runserver   # terminal 2
```

With `DEBUG=True` and no `EMAIL_HOST_USER`, notification emails are printed to the console.

## Checks

```bash
uv run ruff check . && uv run ruff format --check .
uv run python source/manage.py test main_app
```

## Project layout

```
source/
  ironlane/            Django project (config.py = pydantic-settings, settings.py)
  main_app/
    schemas.py         Pydantic schemas for the quote & driver forms
    models.py          QuoteRequest, DriverApplication (managed in /admin)
    notifications.py   Email to dispatch
    templates/         base, index, quote, careers, partials/
  tailwind/input.css   Tailwind source (theme tokens + components)
  static/              compiled CSS, JS, images
```

## Deployment

Same flow as alano_group: pushing to `master` runs lint and tests, builds the Docker
image, pushes it to Docker Hub and restarts `docker compose` on EC2. SQLite lives on the
`db_volume` volume (`DATABASE_PATH=/app/data/db.sqlite3`), so data survives redeploys.

Required GitHub secrets: `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `EC2_HOST`, `EC2_USERNAME`,
`EC2_SSH_KEY`, `SECRET_KEY`, `EMAIL_HOST_USER`, `EMAIL_PASSWORD`.
Optional variables: `ALLOWED_HOSTS`, `ENABLE_HTTPS`, `NGINX_CONF` (use `nginx-http.conf`
until certbot has issued a certificate).
