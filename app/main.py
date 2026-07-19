from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import Response
import yaml

from app.database import init_database
from app.routers import auth, authors, courses, grades

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_database()
    yield


app = FastAPI(title="Course Info API", lifespan=lifespan)
app.include_router(courses.router)
app.include_router(authors.router)
app.include_router(grades.router)
app.include_router(auth.router)


@app.get("/openapi.yml", include_in_schema=False)
def openapi_yaml() -> Response:
    return Response(
        content=yaml.safe_dump(app.openapi(), sort_keys=False),
        media_type="application/yaml",
    )
