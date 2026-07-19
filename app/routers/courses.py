from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Response

from app.models import Course, CourseUpdate
from app.repositories import CourseRepository
from app.security import get_current_user


router = APIRouter(prefix="/courses", tags=["courses"])


def get_course_repository() -> CourseRepository:
    return CourseRepository()


@router.get("", response_model=list[Course])
def get_courses(
    repository: Annotated[CourseRepository, Depends(get_course_repository)],
) -> list[Course]:
    return repository.get_all_courses()


@router.get("/{course_id}", response_model=Course)
def get_course(
    course_id: str,
    repository: Annotated[CourseRepository, Depends(get_course_repository)],
) -> Course:
    course = repository.find_by_id(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return course


@router.post("/{course_id}/notes", status_code=204)
def add_notes(
    course_id: str,
    notes: Annotated[str, Body(media_type="text/plain")],
    repository: Annotated[CourseRepository, Depends(get_course_repository)],
    _user: Annotated[str, Depends(get_current_user)],
) -> Response:
    repository.add_notes(course_id, notes)
    return Response(status_code=204)


@router.post("/", status_code=204)
def post_course(
    course: Course,
    repository: Annotated[CourseRepository, Depends(get_course_repository)],
    _user: Annotated[str, Depends(get_current_user)],
) -> Response:
    repository.save_course(course)
    return Response(status_code=204)


@router.put("/{course_id}", status_code=204)
def put_course(
    course_id: str,
    course: CourseUpdate,
    repository: Annotated[CourseRepository, Depends(get_course_repository)],
    _user: Annotated[str, Depends(get_current_user)],
) -> Response:
    repository.save_course(
        Course(
            id=course_id,
            name=course.name,
            length=course.length,
            url=course.url,
            notes=course.notes,
        )
    )
    return Response(status_code=204)


@router.delete("/{course_id}", status_code=204)
def delete_course(
    course_id: str,
    repository: Annotated[CourseRepository, Depends(get_course_repository)],
    _user: Annotated[str, Depends(get_current_user)],
) -> Response:
    course = repository.find_by_id(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    repository.delete_course(course)
    return Response(status_code=204)
