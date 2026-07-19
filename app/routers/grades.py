from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response

from app.models import Grades, GradesUpdate
from app.repositories import GradesRepository
from app.security import get_current_user


router = APIRouter(prefix="/grades", tags=["grades"])


def get_grades_repository() -> GradesRepository:
    return GradesRepository()


@router.get("", response_model=list[Grades])
def get_grades(
    repository: Annotated[GradesRepository, Depends(get_grades_repository)],
) -> list[Grades]:
    return repository.get_all_grades()


@router.get("/{grade_id}", response_model=Grades)
def get_grade(
    grade_id: int,
    repository: Annotated[GradesRepository, Depends(get_grades_repository)],
) -> Grades:
    grade = repository.find_by_id(grade_id)
    if grade is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return grade


@router.post("/", status_code=204)
def post_grade(
    grade: Grades,
    repository: Annotated[GradesRepository, Depends(get_grades_repository)],
    _user: Annotated[str, Depends(get_current_user)],
) -> Response:
    repository.save_grade(grade)
    return Response(status_code=204)


@router.put("/{grade_id}", status_code=204)
def put_grade(
    grade_id: int,
    grade: GradesUpdate,
    repository: Annotated[GradesRepository, Depends(get_grades_repository)],
    _user: Annotated[str, Depends(get_current_user)],
) -> Response:
    repository.save_grade(
        Grades(
            id=grade_id,
            authorId=grade.authorId,
            courseId=grade.courseId,
            value=grade.value,
        )
    )
    return Response(status_code=204)


@router.delete("/{grade_id}", status_code=204)
def delete_grade(
    grade_id: int,
    repository: Annotated[GradesRepository, Depends(get_grades_repository)],
    _user: Annotated[str, Depends(get_current_user)],
) -> Response:
    grade = repository.find_by_id(grade_id)
    if grade is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    repository.delete_grade(grade)
    return Response(status_code=204)