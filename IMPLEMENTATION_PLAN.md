# FastAPI SQLite Port Plan

## Summary

Create a FastAPI project in `course-info-python` that mirrors the sibling `course-info-spring` REST API and domain model, using Python's built-in `sqlite3` module directly and no SQLAlchemy.

The API mirrors the Spring web controllers:

- `GET /courses`
- `GET /courses/{id}`
- `POST /courses/`
- `PUT /courses/{id}`
- `DELETE /courses/{id}`
- `POST /courses/{id}/notes`
- `GET /authors`
- `GET /authors/{id}` where `{id}` is the author handle

`Calificacion` is included as a domain and repository model for parity with the sibling project, but it does not get REST endpoints because the Spring web module does not expose them.

## Project Structure

Use a lightweight `uv + pyproject.toml` setup:

```text
course-info-python/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── repositories.py
│   └── routers/
│       ├── __init__.py
│       ├── authors.py
│       └── courses.py
├── tests/
│   ├── conftest.py
│   ├── test_authors.py
│   ├── test_courses.py
│   └── test_database.py
├── pyproject.toml
└── README.md
```

Runtime dependencies:

- `fastapi`
- `uvicorn[standard]`

Development/test dependencies:

- `pytest`
- `httpx`

## Domain Models

Define Pydantic models matching the Java records:

- `Course`
  - `id: str`
  - `name: str`
  - `length: int`
  - `url: str`
  - `notes: str | None = None`

- `Author`
  - `id: int | None = None`
  - `firstName: str`
  - `lastName: str`
  - `handle: str`

- `Calificacion`
  - `id: int | None = None`
  - `authorId: int`
  - `courseId: str`
  - `nota: int`

Validation should match the Spring domain records:

- `Course.id`, `Course.name`, and `Course.url` must be non-blank.
- `Course.notes`, when present, must be non-blank.
- `Author.firstName`, `Author.lastName`, and `Author.handle` must be non-blank.
- `Calificacion.courseId` must be non-blank.

Keep JSON field names compatible with the Java API, including camel-case names such as `firstName`, `lastName`, `authorId`, and `courseId`.

## SQLite Backend

Use only Python's built-in `sqlite3` module.

Database behavior:

- Default database path: `./courses.db`
- Override path with `COURSE_INFO_DATABASE`
- Create parent directories for file-backed databases when needed.
- Use `sqlite3.Row` as the row factory.
- Enable foreign key support with `PRAGMA foreign_keys = ON`.
- Initialize schema on application startup.
- Schema initialization must be idempotent.

SQLite schema adapted from `course-info-spring/db_init.sql`:

```sql
CREATE TABLE IF NOT EXISTS courses(
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    length INTEGER NOT NULL,
    url TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS authors(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    handle TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS calificacion(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    author_id INTEGER NOT NULL,
    course_id TEXT NOT NULL,
    nota INTEGER NOT NULL
);
```

## Repository Behavior

Implement repository classes/functions around parameterized SQL.

`CourseRepository`:

- `save_course(course)` inserts or updates by `course.id`.
- `get_all_courses()` returns all courses sorted by `id`.
- `find_by_id(course_id)` returns one course or `None`.
- `add_notes(course_id, notes)` updates only the `notes` column.
- `delete_course(course)` deletes by `course.id`.

`AuthorRepository`:

- `save_author(author)` inserts or updates by unique `handle`.
- `get_all_authors()` returns all authors sorted by `id`.
- `find_by_handle(handle)` returns one author or `None`.

`CalificacionRepository`:

- `save_calificacion(calificacion)` inserts when `id` is missing.
- `save_calificacion(calificacion)` upserts by `id` when `id` is present.
- `get_all_calificaciones()` returns all records sorted by `id`.

Do not add SQLAlchemy, Alembic, or any ORM-style abstraction.

## REST API Behavior

FastAPI app:

- Create the app in `app/main.py`.
- Register the courses and authors routers.
- Initialize the SQLite database in the app lifespan/startup path.

Courses router:

- `GET /courses`
  - Returns `list[Course]`.
  - Sorted by `id`.

- `GET /courses/{course_id}`
  - Returns `Course`.
  - Returns HTTP 404 when missing.

- `POST /courses/`
  - Accepts JSON `Course`.
  - Saves/upserts the course.
  - Returns HTTP 204.

- `PUT /courses/{course_id}`
  - Accepts JSON course data.
  - Ignores any body `id`.
  - Saves the course using the path `course_id`.
  - Returns HTTP 204.

- `DELETE /courses/{course_id}`
  - Finds the course first.
  - Returns HTTP 404 when missing.
  - Deletes existing course.
  - Returns HTTP 204.

- `POST /courses/{course_id}/notes`
  - Consumes `text/plain`.
  - Updates only `notes`.
  - Returns HTTP 204.

Authors router:

- `GET /authors`
  - Returns `list[Author]`.
  - Sorted by `id`.

- `GET /authors/{handle}`
  - Looks up authors by `handle`, matching the Spring controller's `findByHandle` behavior.
  - Returns HTTP 404 when missing.

## Testing Plan

Use `pytest` and FastAPI test client support with a temporary SQLite database per test.

Test setup:

- Use a temp path for `COURSE_INFO_DATABASE`.
- Initialize schema before each test.
- Avoid sharing state between tests.

Course tests:

- Create a course with `POST /courses/`, then fetch it with `GET /courses/{id}`.
- Verify `GET /courses` returns courses sorted by `id`.
- Verify `PUT /courses/{id}` overrides any body `id` with the path id.
- Verify `POST /courses/{id}/notes` consumes plain text and updates notes.
- Verify `DELETE /courses/{id}` removes an existing course.
- Verify missing `GET /courses/{id}` returns 404.
- Verify missing `DELETE /courses/{id}` returns 404.
- Verify blank required course fields return validation errors.
- Verify blank `notes` is rejected when present.

Author tests:

- Seed authors through `AuthorRepository`.
- Verify `GET /authors` returns authors sorted by `id`.
- Verify `GET /authors/{handle}` returns the matching author.
- Verify missing author handle returns 404.
- Verify repository upsert updates an existing author by `handle`.

Database tests:

- Verify schema initialization creates `courses`, `authors`, and `calificacion`.
- Verify schema initialization is idempotent.
- Verify `CalificacionRepository` can persist and list `Calificacion` records.

Verification commands:

```bash
uv sync
uv run pytest
uv run uvicorn app.main:app --reload
```

## Assumptions

- API parity means mirroring the sibling Spring controllers, not exposing every repository as a REST resource.
- `Calificacion` remains domain/repository-only.
- The default database file should be `./courses.db`, matching the sibling project configuration.
- `uv + pyproject.toml` is the intended Python project style.
- The project should preserve Java-compatible JSON field names.
