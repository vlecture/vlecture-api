from .utils import (
  # GENERIC OBJECTS
  NOTE_LANGUAGE,
  TRANSCRIPT,

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


