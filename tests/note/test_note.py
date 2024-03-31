from tests.utils.test_db import (
  client, 
  test_db
)

from tests.utils.login import (
  login_and_token,
)

from tests.note.utils import (
  TRANSCRIPT
)

test_server = "http://staging.api.vlecture.tech"
generate_note_url = "/v1/notes/generate"
get_all_notes_url = "/v1/notes/all"
get_one_note_url = lambda note_id: f"/v1/notes/{note_id}"

login_url = "/v1/auth/login"

# INTEGRATION TESTS FOR NOTES SERVICE
def test_generate_vlecture_note(mongo_test_db):
  # Login
  token = login_and_token(test_db)

  note_title = "My test note"

  headers = {
    'Content-Type': 'application/json', 
    'Authorization': f'Bearer {token}'
  },

  payload = {
    "title": note_title,
    "language": "English",
    "transcript": TRANSCRIPT,
  }

  response = client.post(
    url=generate_note_url,
    headers=headers,
    json=payload,
  )

  result = response.json()

  assert result["title"] == note_title
  