"""FastAPI application entrypoint: middleware and router wiring."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sentri.api.deps import get_bmoni_client, get_synthesizer

__all__ = ["app", "create_app", "get_bmoni_client", "get_synthesizer"]


def create_app() -> FastAPI:
    """Build the Sentri FastAPI application."""
    app = FastAPI(title="Sentri")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from sentri.api.debug import router as debug_router
    from sentri.api.evaluate import router as evaluate_router

    app.include_router(evaluate_router)
    app.include_router(debug_router)

    return app


app = create_app()
