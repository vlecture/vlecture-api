import pytest
from tests.utils.test_db import client, test_db



test_server = "http://staging.api.vlecture.tech"
generate_note_url = "/v1/notes/generate"
get_all_notes_url = "/v1/notes/all"
get_one_note_url = lambda note_id: f"/v1/notes/{note_id}"



