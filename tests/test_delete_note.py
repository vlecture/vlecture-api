from tests.utils.test_db import client, test_db


def test_delete_note_positive(test_db):
    '''Delete your own existing note'''
    response = client.delete("/notes/{note_id}", headers={"Authorization": "Bearer YOUR_ACCESS_TOKEN"})
    assert response.status_code == 200
    assert response.json() == {"message": "Note deleted successfully"}

def test_delete_note_invalid_id(test_db):
    '''Delete your own unexisting note'''
    response = client.delete("/notes/999", headers={"Authorization": "Bearer YOUR_ACCESS_TOKEN"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Note not found"}

def test_delete_note_missing_id(test_db):
    '''Delete your note without any note_id'''
    response = client.delete("/notes/", headers={"Authorization": "Bearer YOUR_ACCESS_TOKEN"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

def test_delete_note_negative(test_db):
    '''Delete someone else's note'''
    response = client.delete("/notes/{note_id}", headers={"Authorization": "Bearer YOUR_ACCESS_TOKEN"})
    assert response.status_code == 403
    assert response.json() == {"detail": "You are not allowed to delete this note"}