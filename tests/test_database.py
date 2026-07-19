from __future__ import annotations

from app.database import connect, init_database
from app.models import Grades
from app.repositories import GradesRepository


def test_database_initialization_creates_expected_tables(db_path: str) -> None:
    init_database(db_path)

    with connect(db_path) as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert {"courses", "authors", "grades"}.issubset(tables)


def test_grades_repository_persists_domain_model(db_path: str) -> None:
    repository = GradesRepository(db_path)

    repository.save_grade(Grades(authorId=1, courseId="course-1", value=5))

    grades = repository.get_all_grades()
    assert len(grades) == 1
    assert grades[0].authorId == 1
    assert grades[0].courseId == "course-1"
    assert grades[0].value == 5