from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from src.utils.db import Base

class AudioFiles(Base):
    __tablename__ = 'audio_files'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    # Define the relationship with the User model
    owner = relationship("User", back_populates="files")
