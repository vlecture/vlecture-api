from sqlalchemy.orm import Session
from src.models.audio_file import AudioFile

from src.schemas.audio_file import AudioFileCreateSchema


def create_audio_file(session: Session, audio_file_data: AudioFileCreateSchema):
    db_audio_file = AudioFile(**audio_file_data.dict())
    session.add(db_audio_file)
    session.commit()
    session.refresh(db_audio_file)
    return db_audio_file
