from unittest.mock import MagicMock

from src.services.note import (
   NoteService,
)

from .utils import (
  # GENERIC OBJECTS
  NOTE_LANGUAGE,
  TRANSCRIPT,

  # INPUTS
  NOTE_ID,

  # OUTPUTS
  EXPECTED_RESPONSE_CONVERT_CORNELL_JSON,
)

def test_convert_text_into_cornell_json(mocker, note_service):
  input_value = {
    "transcript": TRANSCRIPT,
    "language": NOTE_LANGUAGE,
  }

  mocked_api_value = EXPECTED_RESPONSE_CONVERT_CORNELL_JSON
  mocker.patch(
      "src.services.note.NoteService.convert_text_into_cornell_json", 
      return_value=mocked_api_value,
  )

  actual_mock_response = note_service.convert_text_into_cornell_json(
      **input_value
  )

  assert mocked_api_value == actual_mock_response

def test_fetch_note_mongodb():
    input_values = {
        "note_id": NOTE_ID,
    }

    service = NoteService()

    service.fetch_note_from_mongodb = MagicMock()

    service.fetch_note_from_mongodb(**input_values)

    service.fetch_note_from_mongodb.assert_called_once_with(**input_values)