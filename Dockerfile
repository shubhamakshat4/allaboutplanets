# Planetary Status Analyzer — single image serving the API and the built UI.
#
# The FastAPI app mounts frontend/dist itself, so one container serves both on
# one origin. main.py resolves that directory two levels up from backend/app/,
# which is why the frontend build is copied to /app/frontend/dist below.

# --------------------------------------------------------------------------
# Stage 1: build the React frontend
# --------------------------------------------------------------------------
FROM node:20-slim AS frontend

WORKDIR /app/frontend

# Copy the manifests first so the dependency layer is cached until they change.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


# --------------------------------------------------------------------------
# Stage 2: Python runtime
# --------------------------------------------------------------------------
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt

# PyJHora declares PyQt6 for its desktop UI module, which this application
# never imports. Installing it with --no-deps and supplying its real runtime
# needs (swisseph, geopy, pytz, listed in requirements.txt) keeps roughly
# 100 MB of Qt out of the image.
RUN pip install --no-deps PyJHora==4.8.7 \
 && pip install -r backend/requirements.txt

COPY backend/ backend/
COPY --from=frontend /app/frontend/dist frontend/dist

# Fail the build rather than the deploy if the UI did not land where the app
# expects it. main.py reports frontend_bundled on /health for the same reason.
RUN test -f frontend/dist/index.html

# Run as a non-root user.
RUN useradd --create-home --uid 10001 appuser \
 && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/backend

# Render supplies PORT; the default keeps `docker run -p 8000:8000` working.
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
