from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from src.utils.db import Base

class AudioFile(Base):
    __tablename__ = 'audio_file'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="files")
