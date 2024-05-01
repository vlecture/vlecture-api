### UNIT TESTS FOR NOTES SERVICES
import pytest
from openai import (
  OpenAI
)

from tests.utils.test_db import client, test_db

from src.schemas.note import (
  NoteBlockSchema,
  NoteSchema,
)

from .utils import (
  # INPUTS
  INPUT_FORMAT_CORNELL_INTO_BLOCKNOTE_ARRAY,
  INPUT_CREATE_NOTEBLOCK,
  INPUT_GENERATE_NOTE_FROM_TRANSCRIPTION,
)

# Source: https://pytest-with-eric.com/introduction/python-testing-strategy/

# Incoming Query Messages
def test_get_openai(note_service):
  openai_client = note_service.get_openai()

  assert isinstance(openai_client, OpenAI)


def test_create_paragraph_block_from_text(mocker, note_service):
  actual_response = note_service.create_paragraph_block_from_text(
    text="Hello world!"
  )

  assert isinstance(actual_response, NoteBlockSchema)

def test_create_note_block_object(note_service):
  input_value = INPUT_CREATE_NOTEBLOCK
  
  actual_mock_response = note_service.create_note_block_object(
      **input_value 
  )

  assert isinstance(actual_mock_response, NoteSchema)


def test_format_cornell_section_into_blocknote_array(note_service):
  input_value = INPUT_FORMAT_CORNELL_INTO_BLOCKNOTE_ARRAY
  
  actual_response = note_service.format_cornell_section_into_blocknote_array(
      **input_value
  )

  assert actual_response[0].content[0]["text"] == input_value["payload"][0]

def test_get_word_count_str_array(note_service):
  input_value = {
    "str_list": [
      "Hello world",
      "Lorem ipsum"
    ]
  }

  # We expect there are a total of 2 + 2 = 4 words
  EXPECTED_RESPONSE = 4

  actual_response = note_service.get_word_count_str_array(
    **input_value
  )

  assert actual_response == EXPECTED_RESPONSE

# def test_generate_note_from_transcription(note_service):
#   input_value = {
#     "payload": INPUT_GENERATE_NOTE_FROM_TRANSCRIPTION,
#   }

#   actual_response = note_service.generate_note_from_transcription(
#     **input_value
#   )

#   assert isinstance(actual_response, NoteSchema)

