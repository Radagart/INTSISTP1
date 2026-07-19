from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models import Token, UserCreate, UserOut
from app.repositories import UserRepository
from app.security import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_repository() -> UserRepository:
    return UserRepository()


@router.post("/register", response_model=UserOut, status_code=201)
def register(
    user: UserCreate,
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserOut:
    if repository.find_by_username(user.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    hashed_password = hash_password(user.password)
    repository.save_user(user.username, hashed_password)

    created = repository.find_by_username(user.username)
    assert created is not None
    user_id, username, _ = created
    return UserOut(id=user_id, username=username)


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> Token:
    existing = repository.find_by_username(form_data.username)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    _, username, hashed_password = existing
    if not verify_password(form_data.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(username)
    return Token(access_token=access_token, token_type="bearer")