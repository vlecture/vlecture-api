import uuid
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.usages import Usage

class UsageService():
    
    def get_current_usage(self, session: Session, user_id: str):
        print("!!!getting usage obj")
        return session.query(Usage).filter(Usage.user_id == user_id) \
                                    .order_by(desc(Usage.created_at)).first()

    def get_current_usage_quota(self, session: Session, user_id: str):
        print("!!!getting quota")
        usage = self.get_current_usage(session, user_id)

        print("!!!lets go")

        # return  {"quota": usage.quota}
        return usage.quota