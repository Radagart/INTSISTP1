from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


def _filled(value: str) -> str:
    if value is None or not value.strip():
        raise ValueError("No value present!!")
    return value


class Course(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    length: int
    url: str
    notes: str | None = None

    @field_validator("id", "name", "url")
    @classmethod
    def required_text_must_be_filled(cls, value: str) -> str:
        return _filled(value)

    @field_validator("notes")
    @classmethod
    def optional_notes_must_be_filled(cls, value: str | None) -> str | None:
        if value is not None:
            return _filled(value)
        return value


class CourseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    name: str
    length: int
    url: str
    notes: str | None = None

    @field_validator("id", "name", "url")
    @classmethod
    def text_must_be_filled(cls, value: str | None) -> str | None:
        if value is not None:
            return _filled(value)
        return value

    @field_validator("notes")
    @classmethod
    def optional_notes_must_be_filled(cls, value: str | None) -> str | None:
        if value is not None:
            return _filled(value)
        return value


class Author(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int | None = None
    firstName: str
    lastName: str
    handle: str

    @field_validator("firstName", "lastName", "handle")
    @classmethod
    def required_text_must_be_filled(cls, value: str) -> str:
        return _filled(value)


class Grades(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int | None = None
    authorId: int
    courseId: str
    value: int

    @field_validator("courseId")
    @classmethod
    def course_id_must_be_filled(cls, value: str) -> str:
        return _filled(value)

class GradesUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int | None = None
    authorId: int
    courseId: str
    value: int

    @field_validator("courseId")
    @classmethod
    def course_id_must_be_filled(cls, value: str) -> str:
        return _filled(value)

class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    password: str

    @field_validator("username", "password")
    @classmethod
    def required_text_must_be_filled(cls, value: str) -> str:
        return _filled(value)


class UserOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"        

def course_from_row(row: Any) -> Course:
    return Course(
        id=row["id"],
        name=row["name"],
        length=row["length"],
        url=row["url"],
        notes=row["notes"],
    )


def author_from_row(row: Any) -> Author:
    return Author(
        id=row["id"],
        firstName=row["firstName"],
        lastName=row["lastName"],
        handle=row["handle"],
    )


def grade_from_row(row: Any) -> Grades:
    return Grades(
        id=row["id"],
        authorId=row["author_id"],
        courseId=row["course_id"],
        value=row["value"],
    )


def user_from_row(row: Any) -> tuple[int, str, str]:
    return row["id"], row["username"], row["hashed_password"]


