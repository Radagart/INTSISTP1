from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.database import DATABASE_ENV_VAR, init_database
from app.main import app


@pytest.fixture()
def db_path(tmp_path) -> Iterator[str]:
    path = str(tmp_path / "courses.db")
    previous = os.environ.get(DATABASE_ENV_VAR)
    os.environ[DATABASE_ENV_VAR] = path
    init_database(path)
    try:
        yield path
    finally:
        if previous is None:
            os.environ.pop(DATABASE_ENV_VAR, None)
        else:
            os.environ[DATABASE_ENV_VAR] = previous


@pytest.fixture()
def client(db_path: str) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    client.post(
        "/auth/register",
        json={"username": "tester", "password": "testpass123"},
    )
    response = client.post(
        "/auth/login",
        data={"username": "tester", "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}