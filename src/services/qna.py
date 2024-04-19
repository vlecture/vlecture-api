from openai import (
  OpenAI
)

from fastapi import (
  Request,
)

import re
import uuid
from uuid import UUID

import time
import json
import requests
import pytz
from datetime import datetime
from bson import ObjectId

from sqlalchemy.orm import Session
from typing import List, Union
from botocore.exceptions import ClientError

from src.models.users import User

from src.schemas.note import (
  NoteSchema
)

class QNAService:
  def generate_qna_set(
    self, 
    note: NoteSchema,
    question_count: int,
    user: User,
  ):
    pass