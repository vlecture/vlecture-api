from openai import (
  OpenAI
)

import uuid
from uuid import UUID

import time
import json
import requests
import pytz
from datetime import datetime

from sqlalchemy.orm import Session
from typing import List, Union
from botocore.exceptions import ClientError

from src.schemas.note import (
  # OBJ SCHEMA
  LLMCornellNoteFromTranscript,
  BlockNoteCornellSchema,
  NoteSchema,
  NoteBlockSchema,

  # REQ SCHEMA
  GenerateNoteServiceRequestSchema,
)

from src.utils.time import get_datetime_now_jkt

from src.utils.settings import (
  OPENAI_API_KEY,
  OPENAI_ORG_ID,
  OPENAI_MODEL_NAME,
)

from src.utils.openai import (
  construct_system_instructions
)

class NoteService:
  MODEL_TEMPERATURE = 0.7

  def __init__(self) -> None:
    # Init OpenAI Client
    self.openai_client = OpenAI(
      api_key=OPENAI_API_KEY,
      organization=OPENAI_ORG_ID,
    ) 

  def get_openai(self):
    return self.openai_client
  
  def convert_text_into_cornell_json(
      self, 
      transcript: str
  ) -> LLMCornellNoteFromTranscript:
    client = self.get_openai()

    SYSTEM_PROMPT = construct_system_instructions(context=transcript)
    
    chat_completion = client.chat.completions.create(
      model=OPENAI_MODEL_NAME,
      temperature=self.MODEL_TEMPERATURE,
      messages=[
        {
          "role": "system",
          "content": SYSTEM_PROMPT,
        }
      ]
    )

    llm_answer = chat_completion.choices[0].message.content
    llm_answer: LLMCornellNoteFromTranscript = json.loads(llm_answer)

    return llm_answer
  
  def create_paragraph_block_from_text(self, text: str) -> NoteBlockSchema:
    return NoteBlockSchema(
      id=uuid.uuid4(),
      type="paragraph",
      props={
        "textColor": "default",
        "backgroundColor": "default",
        "textAlignment": "left"
      },
      content=[
        {
          "type": "text",
          "text": f"{text}",
          "styles": {}
        }
      ],
      children=[]
    )
  
  def create_note_block_object(
      self, 
      owner_id: UUID,
      title: str,
      main: List[NoteBlockSchema],
      cues: List[NoteBlockSchema],
      summary: List[NoteBlockSchema],
      subtitle: str = "",
  ) -> NoteSchema:
    datetime_now_jkt = get_datetime_now_jkt()

    new_note_object = NoteSchema(
      owner_id=owner_id,
      title=title,
      subtitle=subtitle,
      created_at=datetime_now_jkt,
      updated_at=datetime_now_jkt,
      is_deleted=False,
      is_edited=False,
      is_published=False,
      main=main,
      cues=cues,
      summary=summary,
    )

    return new_note_object
  
  def format_cornell_section_into_blocknote_array(
      self, 
      payload: List[str]
  ) -> List[NoteBlockSchema]:
    blocknote_json: List[NoteBlockSchema] = []

    # Create an array of regular Paragraph Block components
    for text_chunk in payload:
      blocknote_chunk_json = self.create_paragraph_block_from_text(text=str(text_chunk))

      blocknote_json.append(blocknote_chunk_json)

    return blocknote_json
  
  def store_note_to_mongodb(self, note: BlockNoteCornellSchema):
    # TODO
    pass

  def generate_note_from_transcription(
      self, 
      payload: GenerateNoteServiceRequestSchema
  ) -> NoteSchema:
    transcript = payload.transcript
    title = payload.title
    owner_id = payload.owner_id 

    note_json = self.convert_text_into_cornell_json(transcript=transcript)

    main_blocknote = self.format_cornell_section_into_blocknote_array(payload=note_json["main"])

    cues_blocknote = self.format_cornell_section_into_blocknote_array(payload=note_json["cues"])

    summary_blocknote = self.format_cornell_section_into_blocknote_array(payload=note_json["summary"])

    # Create NoteSchema and return it
    new_note_object = self.create_note_block_object(
      owner_id=owner_id,
      title=title,
      main=main_blocknote,
      cues=cues_blocknote,
      summary=summary_blocknote,
      subtitle="", # Init subtitle to empty
    )

    return new_note_object
    
    