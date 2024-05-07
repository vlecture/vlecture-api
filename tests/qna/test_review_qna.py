# from tests.utils.test_db import client, test_db
# from datetime import datetime
# from fastapi.testclient import TestClient
# from unittest.mock import patch
# from bson import ObjectId

# from src.models import QNASetReviewPayloadSchema, QNASetReviewSchema

# from .utils import (
#   # INPUTS
#   OWNER_ID,
#   NOTE_ID,
#   QNA_SET_ID,
#   QUESTION_ID,
#   CORRECT_ANSWER_ID
# )


# # Positive Cases

# def test_review_qna_positive(test_db):
#     payload = QNASetReviewPayloadSchema(
#         owner_id=OWNER_ID,
#         note_id=NOTE_ID,
#         qna_set_id=QNA_SET_ID,
#         answers=[
#             {"question_id": QUESTION_ID, "answer_id": CORRECT_ANSWER_ID, "created_at": datetime.now()}
#         ],
#         created_at=datetime.now(),
#     )

#     response = client.post("/review", json=payload.dict())

#     assert response.status_code == 200
#     assert "uuid" in response.json()
#     assert response.json()["note_id"] == NOTE_ID

# # Negative Cases

# def test_review_qna_invalid_qna_set_id(test_db):
#     payload = QNASetReviewPayloadSchema(
#         owner_id=OWNER_ID,
#         note_id=NOTE_ID,
#         qna_set_id="123asdf",
#         answers=[
#             {"question_id": QUESTION_ID, "answer_id": CORRECT_ANSWER_ID, "created_at": datetime.now()}
#         ],
#         created_at=datetime.now(),
#     )

#     response = client.post("/review-qna", json=payload.dict())

#     assert response.status_code == 404

# # Corner Cases

# def test_review_qna_empty_answers(test_db):
#     payload = QNASetReviewPayloadSchema(
#         owner_id=OWNER_ID,
#         note_id=NOTE_ID,
#         qna_set_id=QNA_SET_ID,
#         answers=[],  # Empty answers list
#         created_at=datetime.now(),
#     )

#     response = client.post("/review-qna", json=payload.dict())

#     assert response.status_code == 200
#     assert "uuid" in response.json()
#     assert response.json()["note_id"] == NOTE_ID
