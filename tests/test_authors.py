from __future__ import annotations

from fastapi.testclient import TestClient

from app.models import Author
from app.repositories import AuthorRepository


def test_get_authors_sorted_by_id(client: TestClient, db_path: str) -> None:
    repository = AuthorRepository(db_path)
    repository.save_author(Author(firstName="Ada", lastName="Lovelace", handle="ada"))
    repository.save_author(Author(firstName="Grace", lastName="Hopper", handle="grace"))

    response = client.get("/authors")

    assert response.status_code == 200
    assert [author["handle"] for author in response.json()] == ["ada", "grace"]


def test_get_author_by_handle(client: TestClient, db_path: str) -> None:
    repository = AuthorRepository(db_path)
    repository.save_author(Author(firstName="Ada", lastName="Lovelace", handle="ada"))

    response = client.get("/authors/ada")

    assert response.status_code == 200
    assert response.json()["firstName"] == "Ada"
    assert response.json()["handle"] == "ada"


def test_missing_author_returns_404(client: TestClient) -> None:
    response = client.get("/authors/missing")

    assert response.status_code == 404


def test_author_upsert_uses_handle(db_path: str) -> None:
    repository = AuthorRepository(db_path)
    repository.save_author(Author(firstName="Ada", lastName="Lovelace", handle="ada"))
    repository.save_author(Author(firstName="Augusta", lastName="King", handle="ada"))

    authors = repository.get_all_authors()

    assert len(authors) == 1
    assert authors[0].firstName == "Augusta"
    assert authors[0].lastName == "King"
