from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.models import Author
from app.repositories import AuthorRepository



router = APIRouter(prefix="/authors", tags=["authors"])


def get_author_repository() -> AuthorRepository:
    return AuthorRepository()


@router.get("", response_model=list[Author])
def get_authors(
    repository: Annotated[AuthorRepository, Depends(get_author_repository)],
) -> list[Author]:
    return repository.get_all_authors()


@router.get("/{handle}", response_model=Author)
def get_author(
    handle: str,
    repository: Annotated[AuthorRepository, Depends(get_author_repository)],
) -> Author:
    author = repository.find_by_handle(handle)
    if author is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return author
