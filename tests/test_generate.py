from tests.utils.test_db import client


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200


def test_delete_flashcard_set_positive():

    response = client.delete("/v1/flashcards/set/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Flashcard set successfully deleted."


def test_delete_flashcard_set_unauthorized_user():
    # Login sebagai user dengan id 2 atau set header Authorization
    response = client.delete(
        "/v1/flashcards/set/1"
    )  # Menggunakan id set yang sama dengan test sebelumnya
    assert response.status_code == 403
    assert "Unauthorized" in response.json()["error"]


def test_delete_nonexistent_flashcard_set():
    response = client.delete("/v1/flashcards/set/999")
    # Menggunakan id tidak ada
    assert response.status_code == 404
    assert (
        "not found" in response.json()["error"]
        or "doesn't exist" in response.json()["error"]
    )
