"""Planetary Status Analyzer — FastAPI application.

Calculate, organise, display. This service performs no interpretation and
generates no predictions.
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.routes import router

# The built frontend, when `npm run build` has been run. Serving it from here
# gives a single origin for the whole application, so no proxy or CORS is
# involved in a hosted run.
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("planetary_status_analyzer")

app = FastAPI(
    title="Planetary Status Analyzer",
    version="1.0.0",
    description=(
        "Calculates a Vedic astrology chart with PyJHora and exposes structured, "
        "factual planetary analysis. No predictions, no interpretation."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:4173", "http://127.0.0.1:4173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    logger.warning("ValueError on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {exc}"},
    )


@app.get("/health")
def health() -> dict:
    from .astrology import pyjhora_adapter as adapter
    return {
        "status": "ok",
        "pyjhora_version": adapter.PYJHORA_VERSION,
        "ephemeris": adapter.EPHEMERIS_NAME,
        "frontend_bundled": FRONTEND_DIST.is_dir(),
    }


# ---------------------------------------------------------------------------
# Serve the built single-page app, if it has been built.
#
# Mounted last so that /api and /health always win. Unknown paths fall back to
# index.html, which is what a single-page app needs on a hard refresh; unknown
# /api paths still return a JSON 404 rather than HTML.
# ---------------------------------------------------------------------------
if FRONTEND_DIST.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="assets",
    )

    @app.get("/", include_in_schema=False)
    def serve_index() -> FileResponse:
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str) -> FileResponse:
        if full_path.startswith(("api/", "health", "docs", "openapi.json", "redoc")):
            raise HTTPException(status_code=404, detail="Not found")
        candidate = (FRONTEND_DIST / full_path).resolve()
        # Serve a real static file when one exists, but never escape the bundle.
        if (candidate.is_file()
                and FRONTEND_DIST.resolve() in candidate.parents):
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    logger.info(
        "No frontend build found at %s. Run `npm run build` in frontend/ to "
        "serve the UI from this process, or use the Vite dev server.",
        FRONTEND_DIST,
    )
