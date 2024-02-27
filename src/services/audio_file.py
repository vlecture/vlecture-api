from sqlalchemy.orm import Session
from src.models.audio_file import AudioFile

from src.schemas.audio_file import AudioFileSchema


def create_audio_file(session: Session, audio_file_data: dict):
    # Create an AudioFile instance using the provided data
    audio_file = AudioFile(**audio_file_data)

    # Add the instance to the session and commit the changes
    session.add(audio_file)
    session.commit()

    # Refresh the instance to ensure it reflects the changes made in the database
    session.refresh(audio_file)

    return audio_file
