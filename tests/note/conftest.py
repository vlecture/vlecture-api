import pytest
from src.services.note import (
  NoteService
)

@pytest.fixture(scope="session")
def note_service():
  """
  Create Note Service object
  """

  note_service = NoteService()
  return note_service

