import uuid
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.usages import Usage

class UsageService():
    
    def get_current_usage(self, session: Session, user_id: str):
        print("getting usage object...")
        return session.query(Usage).filter(Usage.user_id == user_id) \
                                    .order_by(desc(Usage.created_at)).first()
    
    def update_quota(self, session: Session, usage: Usage):
        print("Updating quota...")
        usage.quota -= 1        
        session.commit()
