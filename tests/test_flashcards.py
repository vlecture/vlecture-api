import pytest
import requests

fetch_flashcard_sets_url = "/v1/flashcards"
fetch_flashcards_url = "/v1/flashcards/set"  
test_server = "http://staging.api.vlecture.tech"

AUTH_HEADER = {
    "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmaXJzdF9uYW1lIjoibWFuZGEiLCJlbWFpbCI6Im1hbmRhdGVzQGdtYWlsLmNvbSIsImV4cCI6MTcxMTI0ODgxOX0.qrMHZkrM6wEFK_0LzkXqchCk1Dv6gSkt3qtnVIdDuvo"
}
VALID_USER_ID = "5acb2e38-0636-4b71-a468-fd695b5d4a27"
VALID_USER_ID_NO_SET = "5acb2e38-0636-4b71-a468-fd695b5d4a00"
VALID_NOTE_ID = "5acb2e38-0636-4b71-a468-fd695b5d4a26"
VALID_SET_ID = "5acb2e38-0636-4b71-a468-fd695b5d4a25"

# Positive Cases
@pytest.mark.anyio
def test_fetch_flashcard_sets_positive(test_db):
    response = requests.get(
        test_server + fetch_flashcard_sets_url, 
        headers=AUTH_HEADER,
        json={"user_id" : VALID_USER_ID}
    )

    assert response.status_code == 200
    assert response.json()['message'] == "Succesfully fetched all flashcard sets from current user."

@pytest.mark.anyio
def test_fetch_flashcards_positive(test_db):
    response = requests.get(
        test_server + fetch_flashcards_url, 
        headers=AUTH_HEADER,
        json={"note_id" : VALID_NOTE_ID, "set_id": VALID_SET_ID}
    )
   
    assert response.status_code == 200
    assert response.json()['message'] == "Succesfully fetched all flashcards from set."
    
# Negative Cases
@pytest.mark.anyio
def test_fetch_flashcard_sets_not_logged_in(test_db):
    response = requests.get(
        test_server + fetch_flashcard_sets_url, 
        json={"user_id" : VALID_USER_ID}
    )

    assert response.status_code == 401 
    assert response.json()['error'] == "You don't have access to these flashcard sets or flashcard sets don't exist."

@pytest.mark.anyio
def test_fetch_flashcards_not_logged_in(test_db):
    response = requests.get(
        test_server + fetch_flashcards_url, 
        json={"note_id" : VALID_NOTE_ID, "set_id": VALID_SET_ID}
    )

    assert response.status_code == 401
    assert response.json()['error'] == "You don't have access to these flashcards or flashcards don't exist."

# Edge Cases
@pytest.mark.anyio
def test_fetch_flashcard_sets_no_sets(test_db):
    response = requests.get(
        test_server + fetch_flashcard_sets_url, 
        headers=AUTH_HEADER,
        json={"user_id" : VALID_USER_ID_NO_SET}
    )

    assert response.status_code == 200
    assert response.json()['message'] == "Succesfully fetched all flashcard sets from current user."

