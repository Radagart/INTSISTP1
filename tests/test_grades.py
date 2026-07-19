from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_and_get_grade(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/grades/",
        json={"authorId": 1, "courseId": "python101", "value": 95},
        headers=auth_headers,
    )
    assert response.status_code == 204

    response = client.get("/grades")
    assert response.status_code == 200

    grades = response.json()
    assert len(grades) == 1
    created = grades[0]
    assert created["authorId"] == 1
    assert created["courseId"] == "python101"
    assert created["value"] == 95

    response = client.get(f"/grades/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_grades_are_sorted_by_id(client: TestClient, auth_headers: dict[str, str]) -> None:
    client.post("/grades/", json={"authorId": 1, "courseId": "python101", "value": 80}, headers=auth_headers)
    client.post("/grades/", json={"authorId": 2, "courseId": "fastapi201", "value": 90}, headers=auth_headers)

    response = client.get("/grades")

    assert response.status_code == 200
    ids = [grade["id"] for grade in response.json()]
    assert ids == sorted(ids)


def test_update_uses_path_id(client: TestClient, auth_headers: dict[str, str]) -> None:
    client.post("/grades/", json={"authorId": 1, "courseId": "python101", "value": 80}, headers=auth_headers)
    grade_id = client.get("/grades").json()[0]["id"]

    response = client.put(
        f"/grades/{grade_id}",
        json={"id": 999, "authorId": 2, "courseId": "fastapi201", "value": 100},
        headers=auth_headers,
    )
    assert response.status_code == 204

    response = client.get(f"/grades/{grade_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": grade_id,
        "authorId": 2,
        "courseId": "fastapi201",
        "value": 100,
    }


def test_delete_existing_grade(client: TestClient, auth_headers: dict[str, str]) -> None:
    client.post("/grades/", json={"authorId": 1, "courseId": "python101", "value": 80}, headers=auth_headers)
    grade_id = client.get("/grades").json()[0]["id"]

    response = client.delete(f"/grades/{grade_id}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/grades/{grade_id}")
    assert response.status_code == 404


def test_missing_grade_returns_404(client: TestClient, auth_headers: dict[str, str]) -> None:
    assert client.get("/grades/9999").status_code == 404
    assert client.delete("/grades/9999", headers=auth_headers).status_code == 404


def test_blank_course_id_is_rejected(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/grades/",
        json={"authorId": 1, "courseId": " ", "value": 80},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_write_endpoints_require_authentication(client: TestClient) -> None:
    response = client.post(
        "/grades/",
        json={"authorId": 1, "courseId": "python101", "value": 80},
    )
    assert response.status_code == 401