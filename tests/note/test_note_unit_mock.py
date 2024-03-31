import pytest
import pytest_mock

from .utils import (
  # GENERIC OBJECTS
  NOTE_LANGUAGE,
  TRANSCRIPT,

  # OUTPUTS
  EXPECTED_RESPONSE_CONVERT_CORNELL_JSON,
  EXPECTED_RESPONSE_CREATE_PARAGRAPH_BLOCK,
  EXPECTED_RESPONSE_CREATE_NOTEBLOCK,
  EXPECTED_RESPONSE_FORMAT_CORNELL_INTO_BLOCKNOTE_ARRAY_OLD,
  EXPECTED_RESPONSE_GENERATE_NOTE,
  

  # INPUTS
  INPUT_CREATE_NOTEBLOCK,
  INPUT_FORMAT_CORNELL_INTO_BLOCKNOTE_ARRAY,
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


