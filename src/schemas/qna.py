from uuid import UUID
from datetime import datetime

from bson.objectid import (
  ObjectId
)

from typing import (
  Annotated,
  Optional,
  List,
  Any
)

from pydantic import (
  BaseModel, 
  BeforeValidator,
  Field,
  ConfigDict,
)

from pydantic_core import core_schema

PyObjectId = Annotated[str, BeforeValidator(str)]

class PydanticObjectId(str):
  """
  Pydantic-compatible MongoDB ObjectId type

  Ref: https://stackoverflow.com/questions/76686888/using-bson-objectid-in-pydantic-v2
  """
  @classmethod
  def __get_pydantic_core_schema__(
    cls,
    _source_type: Any,
    _handler: Any,
  ) -> core_schema.CoreSchema:
    return core_schema.json_or_python_schema(
      json_schema=core_schema.str_schema(),
      python_schema=core_schema.union_schema([
        core_schema.is_instance_schema(ObjectId),
        core_schema.chain_schema([
          core_schema.str_schema(),
          core_schema.no_info_plain_validator_function(cls.validate),
        ])
      ]),
      serialization=core_schema.plain_serializer_function_ser_schema(
        lambda x: str(x)
      ),
    )
  
  @classmethod
  def validate(cls, value) -> ObjectId:
    if not ObjectId.is_valid(value):
      raise ValueError("Invalid ObjectId")
    
    return ObjectId(value)

# GENERATE QNA
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
  qna_set_uuid: UUID

  created_at: datetime
  updated_at: datetime 
  is_deleted: bool = Field(default=False)

  
  question: str
  answer_options: List[QNAAnswerSchema] # 4 items
  answer_key: QNAAnswerSchema # 1

  question_score: float

  marked_irrelevant: bool = Field(default=False)

class QNAQuestionSetSchema(BaseModel):
  """
  Object schema for a Set of QnA Questions
  """

  id: Optional[PyObjectId] = Field(alias="_id", default=None)
  
  # Create a new field UUID to identify MongoDB objects
  uuid: UUID
  owner_id: UUID
  note_id: str

  created_at: datetime
  updated_at: datetime 
  is_deleted: bool = Field(default=False)
  
  question_count: int
  questions: List[QNAQuestionSchema]

  model_config = ConfigDict(
    populate_by_name=True,
    arbitrary_types_allowed=True,
  )

# REVIEW QNA
class QNAQuestionReviewSchema(BaseModel):
  """
  Schema for Review QnA Question object
  """

  id: UUID
  qna_set_review_uuid: UUID

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

  id: Optional[PyObjectId] = Field(alias="_id", default=None)

  uuid: UUID
  note_id: str
  
  # created_at here serves as the "answered at" time for a QNA Set 
  # (when the user submits a QNA Set)
  created_at: datetime
  updated_at: datetime
  is_deleted: bool = Field(default=False)

  qna_set_id: UUID
  correctly_answered_q: List[QNAQuestionReviewSchema]
  incorrectly_answered_q: List[QNAQuestionReviewSchema]

  score_obtained: float

  model_config = ConfigDict(
    populate_by_name=True,
    arbitrary_types_allowed=True,
  )
  
class QNAUserAnswerPayloadSchema(BaseModel):
  id: UUID

  question_id: UUID
  answer_id: UUID
  created_at: datetime

class QNASetReviewPayloadSchema(BaseModel):
  id: UUID

  owner_id: UUID
  note_id: str
  qna_set_id: UUID
  created_at: datetime
  answers: List[QNAUserAnswerPayloadSchema]


# REQUEST SCHEMAS
class GenerateQNASetRequestSchema(BaseModel):
  """
  Schema for the Request object of Generate Note
  
  Example:

  {
    "note_id": "632883282481232",
    "question_count": 3,
  }
  """

  note_id: str
  question_count: int
  

# RESPONSE SCHEMAS

