from __future__ import annotations

from app.database import connect
from app.models import (
    Author,
    Grades,
    Course,
    author_from_row,
    grade_from_row,
    course_from_row,
    user_from_row,
)


class CourseRepository:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path

    def save_course(self, course: Course) -> None:
        with connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO courses (id, name, length, url, notes)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    length = excluded.length,
                    url = excluded.url,
                    notes = excluded.notes
                """,
                (course.id, course.name, course.length, course.url, course.notes),
            )

    def get_all_courses(self) -> list[Course]:
        with connect(self.db_path) as connection:
            rows = connection.execute("SELECT * FROM courses ORDER BY id").fetchall()
        return [course_from_row(row) for row in rows]

    def add_notes(self, course_id: str, notes: str) -> None:
        with connect(self.db_path) as connection:
            connection.execute(
                "UPDATE courses SET notes = ? WHERE id = ?",
                (notes, course_id),
            )

    def delete_course(self, course: Course) -> None:
        with connect(self.db_path) as connection:
            connection.execute("DELETE FROM courses WHERE id = ?", (course.id,))

    def find_by_id(self, course_id: str) -> Course | None:
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM courses WHERE id = ? LIMIT 1",
                (course_id,),
            ).fetchone()
        if row is None:
            return None
        return course_from_row(row)


class AuthorRepository:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path

    def save_author(self, author: Author) -> None:
        with connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO authors (firstName, lastName, handle)
                VALUES (?, ?, ?)
                ON CONFLICT(handle) DO UPDATE SET
                    firstName = excluded.firstName,
                    lastName = excluded.lastName
                """,
                (author.firstName, author.lastName, author.handle),
            )

    def get_all_authors(self) -> list[Author]:
        with connect(self.db_path) as connection:
            rows = connection.execute("SELECT * FROM authors ORDER BY id").fetchall()
        return [author_from_row(row) for row in rows]

    def find_by_handle(self, handle: str) -> Author | None:
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM authors WHERE handle = ? LIMIT 1",
                (handle,),
            ).fetchone()
        if row is None:
            return None
        return author_from_row(row)


class GradesRepository:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path

    def save_grade(self, grade: Grades) -> None:
        with connect(self.db_path) as connection:
            if grade.id is None:
                connection.execute(
                    """
                    INSERT INTO grades (author_id, course_id, value)
                    VALUES (?, ?, ?)
                    """,
                    (grade.authorId, grade.courseId, grade.value),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO grades (id, author_id, course_id, value)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        author_id = excluded.author_id,
                        course_id = excluded.course_id,
                        value = excluded.value
                    """,
                    (
                        grade.id,
                        grade.authorId,
                        grade.courseId,
                        grade.value,
                    ),
                )

    def get_all_grades(self) -> list[Grades]:
        with connect(self.db_path) as connection:
            rows = connection.execute("SELECT * FROM grades ORDER BY id").fetchall()
        return [grade_from_row(row) for row in rows]

    def find_by_id(self, grade_id: int) -> Grades | None:
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM grades WHERE id = ? LIMIT 1",
                (grade_id,),
            ).fetchone()
        if row is None:
            return None
        return grade_from_row(row)

    def delete_grade(self, grade: Grades) -> None:
        with connect(self.db_path) as connection:
            connection.execute("DELETE FROM grades WHERE id = ?", (grade.id,))

class UserRepository:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path

    def save_user(self, username: str, hashed_password: str) -> None:
        with connect(self.db_path) as connection:
            connection.execute(
                "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
                (username, hashed_password),
            )

    def find_by_username(self, username: str) -> tuple[int, str, str] | None:
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE username = ? LIMIT 1",
                (username,),
            ).fetchone()
        if row is None:
            return None
        return user_from_row(row)            