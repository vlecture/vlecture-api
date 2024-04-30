from unittest.mock import MagicMock
from src.services.note import NoteService

from .utils import NOTE_ID

def test_delete_note_positive(mongo_test_db):
    """Test to delete your own existing note"""
    service = NoteService()
    service.delete_note_from_mongodb = MagicMock()

    # Simulate the call to delete a note with a valid ID
    service.delete_note_from_mongodb.return_value = True
    response = service.delete_note_from_mongodb(note_id=NOTE_ID)
    assert response == True
    service.delete_note_from_mongodb.assert_called_once_with(note_id=NOTE_ID)

def test_delete_note_negative(mongo_test_db):
    """Test to delete an invalid note ID"""
    service = NoteService()
    service.delete_note_from_mongodb = MagicMock()

    # Simulate the call to delete a note with an invalid ID case or others' id
    service.delete_note_from_mongodb.return_value = False

    response = service.delete_note_from_mongodb(note_id="invalid_id")
    assert response == False
    service.delete_note_from_mongodb.assert_called_once_with(note_id="invalid_id")