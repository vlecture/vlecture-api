# UNIT TEST FOR QNA
import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient
from main import app  # Ensure this imports the FastAPI app instance

from src.services.qna import QNAService

from .utils import (
    # INPUTS
    NOTE_ID,
    INVALID_NOTE_ID,
    NOTE_MAIN_DATA,
    NOTE_CUES_DATA,
    NOTE_SUMMARY_DATA,
    NOTE_TEXT_SPLITTING_INPUT,
    # OUTPUTS
    EXPECTED_RESPONSE_NOTE_MONGODB,
)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_flatten_note_contents(qna_service):
    input_value = {
        "main": NOTE_MAIN_DATA,
        "cues": NOTE_CUES_DATA,
        "summary": NOTE_SUMMARY_DATA,
    }

    expected_response = f"This is a Cornell-notetaking based Note.\n Note main content:\n{NOTE_MAIN_DATA}\n\nNote cues:\n{NOTE_CUES_DATA}\n\nNote summary: {NOTE_SUMMARY_DATA}"

    actual_response = qna_service.flatten_note_contents(**input_value)

    assert actual_response == expected_response


def test_split_note_into_documents():
    input_values = {
        "text": NOTE_TEXT_SPLITTING_INPUT,
    }

    # Instantiate a local QNAService to avoid global object pollution
    service = QNAService()

    # Mock `split_note_into_documents` method
    service.split_note_into_documents = MagicMock()

    # Call the mocked method with input_values as the parameters
    service.split_note_into_documents(**input_values)

    # Check that the method is called once with the correct arguments
    service.split_note_into_documents.assert_called_once_with(**input_values)


# API Endpoint tests
def test_generate_qna_set_success(client):  # positive
    response = client.post(
        "/v1/qna/generate",
        json={"note_id": NOTE_ID, "question_count": 5},
        headers={"Authorization": "Bearer valid_token"},
    )
    assert response.status_code == 200
    assert "questions" in response.json()
    assert len(response.json()["questions"]) == 5


def test_generate_qna_set_invalid_note_id(client):  # negative
    response = client.post(
        "/v1/qna/generate",
        json={"note_id": INVALID_NOTE_ID, "question_count": 5},
        headers={"Authorization": "Bearer valid_token"},
    )
    assert response.status_code == 404
    assert response.json().get("detail") == "Note not found"


def test_generate_qna_set_zero_questions(client):  # corner case
    response = client.post(
        "/v1/qna/generate",
        json={"note_id": NOTE_ID, "question_count": 0},
        headers={"Authorization": "Bearer valid_token"},
    )
    assert response.status_code == 400
    assert "error" in response.json()
    assert response.json()["error"] == "Question count must be greater than zero"


def test_generate_qna_set_zero_questions_1(client):  # corner case
    response = client.post(
        "/v1/qna/generate",
        json={"note_id": NOTE_ID, "question_count": 3},
        headers={"Authorization": "Bearer valid_token"},
    )
    assert response.status_code == 400
    assert "error" in response.json()
    assert response.json()["error"] == "Question count must be greater than zero"


def test_get_qna_set_by_note_success(client):  # positive
    response = client.get(
        "/v1/qna/{NOTE_ID}", headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 200
    assert "questions" in response.json()


def test_get_qna_set_by_note_not_found(client):  # negative
    response = client.get(
        "/v1/qna/{INVALID_NOTE_ID}", headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 404
    assert "detail" in response.json()
    assert response.json()["detail"] == "QnA set not found"
