# UNIT TEST FOR QNA
import pytest 
from unittest.mock import Mock, MagicMock

from src.services.qna import (
  QNAService
)

from .utils import (
  # INPUTS
  NOTE_ID,
  NOTE_MAIN_DATA,
  NOTE_CUES_DATA,
  NOTE_SUMMARY_DATA,
  NOTE_TEXT_SPLITTING_INPUT,

  # OUTPUTS
  EXPECTED_RESPONSE_NOTE_MONGODB,
)

    
def test_flatten_note_contents(qna_service):
    input_value = {
        "main": NOTE_MAIN_DATA,
        "cues": NOTE_CUES_DATA,
        "summary": NOTE_SUMMARY_DATA,
    }

    expected_response = f"Note main content:\n{NOTE_MAIN_DATA}\n\nNote cues:\n{NOTE_CUES_DATA}\n\nNote summary: {NOTE_SUMMARY_DATA}"

    actual_response = qna_service.flatten_note_contents(
        **input_value
    )

    assert actual_response == expected_response

def test_split_note_into_documents():
    input_values = {
        "text": NOTE_TEXT_SPLITTING_INPUT,
    }

    # Instatiate a local QNAService to avoid global object pollution
    service = QNAService()

    # Mock `note_text_splitting` method
    service.split_note_into_documents = MagicMock()

    # Call the mocked method with input_values as the parameters
    service.split_note_into_documents(**input_values)

    # Check that the method is called once with the correct arguments
    service.split_note_into_documents.assert_called_once_with(**input_values)

