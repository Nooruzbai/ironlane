# --- Stage 1: Build Tailwind CSS ---
FROM node:24-slim AS build-css
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY source ./source
RUN npm run build:css

# --- Stage 2: Run Django ---
FROM python:3.13-slim
# Pin uv instead of :latest so builds are reproducible
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install dependencies first so this layer is cached between code changes
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project --no-cache

COPY source ./source
COPY --from=build-css /app/source/static/css/output.css ./source/static/css/output.css

# Settings refuse the dev secret when DEBUG is off, so pass a throwaway one for this build step
RUN SECRET_KEY=collectstatic-build-only python source/manage.py collectstatic --noinput

RUN useradd --create-home --uid 1000 app && mkdir -p /app/data && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["gunicorn", "--chdir", "source", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-", "ironlane.wsgi:application"]
