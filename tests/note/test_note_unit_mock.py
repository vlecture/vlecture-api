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
  NOTE_BLOCKS,

  # OUTPUTS
  EXPECTED_RESPONSE_CONVERT_CORNELL_JSON,
)

from bson import ObjectId
from src.utils.time import get_datetime_now_jkt

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

# def test_save_note_mongodb():
#   input_values = {
#     "note_id": NOTE_ID,
#     "note_blocks": NOTE_BLOCKS,
#   }
  
#   # Expected output
#   q_filter = {"_id": ObjectId(NOTE_ID)}

#   main = NOTE_BLOCKS["main"]
#   cues = NOTE_BLOCKS["cues"]
#   summary = NOTE_BLOCKS["summary"]

#   service = NoteService()
   
#   # Actual output
#   params = service.generate_save_note_params(
#     **input_values
#   )

#   # Compare actual output against expected output
#   cond_filter_equals = q_filter == params["q_filter"]
#   cond_update_main_equals = main == params["q_update"]["$set"]["main"]
#   cond_update_cues_equals = cues == params["q_update"]["$set"]["cues"]
#   cond_update_summary_equals = summary == params["q_update"]["$set"]["summary"]

#   assert cond_filter_equals \
#     and cond_update_main_equals \
#     and cond_update_cues_equals \
#     and cond_update_summary_equals

