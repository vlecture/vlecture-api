from uuid import UUID
from datetime import datetime

from typing import (
  Optional,
  List,
  Any
)
from pydantic import (
  BaseModel, 
  Field,
)

class QNAAnswerSchema(BaseModel): 
  """
  Object schema for QnA Answer
  """
  
  id: UUID
  created_at: datetime
  updated_at: datetime 
  is_deleted: bool = Field(default=False)

  question_id: UUID

  content: str
  is_correct_answer: bool

class QNAQuestionSchema(BaseModel):
  """
  Object schema for QnA Question object
  """

  id: UUID
  created_at: datetime
  updated_at: datetime 
  is_deleted: bool = Field(default=False)

  qna_set_id: UUID
  
  question: str

  answer_options: List[QNAAnswerSchema]
  answer_key: QNAAnswerSchema

  question_score: float

  marked_irrelevant: bool = Field(default=False)

class QNAQuestionSetSchema(BaseModel):
  """
  Object schema for a Set of QnA Questions
  """

  id: UUID
  created_at: datetime
  updated_at: datetime 
  is_deleted: bool = Field(default=False)
  
  question_count: int
  questions: List[QNAQuestionSchema]


class QNAQuestionReviewSchema(BaseModel):
  """
  Schema for Review QnA Question object
  """

  id: UUID
  created_at: datetime
  updated_at: datetime
  is_deleted: bool = Field(default=False)

  question_id: UUID
  user_answer: QNAAnswerSchema

  is_answered_correctly: bool

  score_obtained: float

class QNASetReviewSchema(BaseModel):
  """
  Schema for Review QnA Question object
  """

  id: UUID
  
  # created_at here serves as the "answered at" time for a QNA Set (when the user attempts a QNA Set)
  created_at: datetime
  updated_at: datetime
  is_deleted: bool = Field(default=False)

  qna_set_id: UUID
  correctly_answered_q: List[QNAQuestionReviewSchema]
  incorrectly_answered_q: List[QNAQuestionReviewSchema]

  score_obtained: float
  