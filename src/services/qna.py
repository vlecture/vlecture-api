from openai import (
  OpenAI
)

from fastapi import (
  Request,
)

from langchain_openai import (
  ChatOpenAI,
  OpenAIEmbeddings
)
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain

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

from src.utils.settings import (
  OPENAI_MODEL_NAME,
  OPENAI_API_KEY,
)

class QNAService:
  MODEL_TEMPERATURE = 0.4

  LLM = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=OPENAI_MODEL_NAME,
    temperature=MODEL_TEMPERATURE,
  )

  def generate_qna_set(
    self, 
    note: NoteSchema,
    question_count: int,
    user: User,
  ):
    note_documents_chunk = self.split_note_into_chunks(
      note=note,
    )

    # Use the OpenAI Embedding model and create Vector Store
    vectorstore = Chroma.from_documents(
      documents=note_documents_chunk,
      embedding=OpenAIEmbeddings(),
    )

    # Convert vectorstore into Retriever interface
    retriever = vectorstore.as_retriever(
      search_type="similarity",
      search_kwargs={
        "k": 6,
      },
    )

    # NOTE - to find the answer to the LLM generated question:
    # retrieved_docs = retriever.invoke("{your_question}"
    BASE_PROMPT = self.get_base_prompt(question_count=question_count)
    REFINED_PROMPT = self.get_refined_prompt(question_count=question_count)

    question_gen_chain = load_summarize_chain(
      llm=self.LLM,
      chain_type="refine",
      verbose=True,
      question_prompt=BASE_PROMPT,
      refine_prompt=REFINED_PROMPT,
    )

    generated_questions = question_gen_chain.run(note_documents_chunk)

    llm_answer_gen = ChatOpenAI(
      temperature=0.2, 
      model=OPENAI_MODEL_NAME, 
      api_key=OPENAI_API_KEY,
    )

    question_list = generated_questions.split("\n")
    
    answer_gen_chain = RetrievalQA.from_chain_type(
      llm=llm_answer_gen,
      chain_type="stuff",
      retriever=retriever,
    )

    # Run answer chain for each question
    answer_list = []
    for question in question_list:
      print("Question:", question)

      answer = answer_gen_chain.run(question)
      answer_list.append(answer)

      print("Answer", answer)
      print("--------------------------------------------------\n\n")

    # Returns the generated questions and answers
    return question_list, answer_list


  def extract_note_sections_to_array(
    self,
    note: NoteSchema,
  ) -> dict:
    sections = ("main", "cues", "summary")
    
    response = {}

    for section in sections:
      section_content = []

      for section_item in note[section]:
        # section_item is a NoteBlockSchema object
        content_arr = section_item["content"]

        for _content in content_arr:
          content = _content["text"]
          section_content.append(content)
      
      # Add section_content to response dict
      response[section] = section_content

    return response

  def flatten_note_contents(
    self,
    note: NoteSchema,
  ) -> str:
    """
    Transforms Note objects into one long string
    """

    note_section_array = self.extract_note_sections_to_array(
      note=note,
    )
    
    main = note_section_array["main"]
    cues = note_section_array["cues"]
    summary = note_section_array["summary"]

    # Format each section
    main_f = "\n".join(main)
    cues_f = "\n".join(cues)
    summary_f = "\n".join(summary)

    response_text = f"This is a Cornell-notetaking based Note. Note main content:\n{main_f}\n\nNote cues:\n{cues_f}\n\nNote summary: {summary_f}"

    return response_text
    
  def split_note_into_chunks(
    self,
    note: NoteSchema,
  ):
    CHUNK_SIZE = 400
    CHUNK_OVERLAP = 60

    recursive_splitter = RecursiveCharacterTextSplitter(
      chunk_size=CHUNK_SIZE,
      chunk_overlap=CHUNK_OVERLAP,
      add_start_index=True,
    )

    # NOTE - the current method flattens a Note's contents into one long string
    # Later, might need to experiment with the input format and compare the results
    note_flattened = self.flatten_note_contents(
      note=note,
    )
    
    # Generate chunk documents
    note_documents_chunk = recursive_splitter.create_documents(
      texts=[note_flattened],
    )

    return note_documents_chunk

  # PROMPT ENGINEERING HELPERS
  def get_base_prompt(self, question_count: int):
    prompt_template = """
    You are an expert at creating quiz questions based on a lecture note.
    Your goal is to prepare a student for their exams based on the notes. 
    You do this by asking questions about the text below:

    ------------
    {text}
    ------------
    """

    prompt_template += f"""
    Create {question_count} AND ONLY {question_count} questions that will prepare the students for their tests.
    Make sure not to lose any important information.

    QUESTIONS:
    """

    print(prompt_template)

    PROMPT_QUESTIONS = PromptTemplate(
      template=prompt_template, 
      input_variables=["text"]
    )

    return PROMPT_QUESTIONS
  
  def get_refined_prompt(self, question_count: int):
    refined_prompt = """
    You are an expert at creating practice questions based on lecture notes.
    Your goal is to help a student prepare for their test.
    You have received some practice questions to a certain extent: 

    {existing_answer}
    
    You have the option to refine the existing questions or add new ones.
    (only if necessary) with some more context below.
    ------------
    {text}
    ------------

    Given the new context, refine the original questions in English.
    If the context is not helpful, please provide the original questions.
    QUESTIONS:
    """

    refined_prompt += f"""
    Create {question_count} AND ONLY {question_count} questions only.
    Given the new context, refine the original questions in English.
    If the context is not helpful, please provide the original questions.

    QUESTIONS:
    """

    REFINE_PROMPT_QUESTIONS = PromptTemplate(
      input_variables=["existing_answer", "text"],
      template=refined_prompt,
    )

    return REFINE_PROMPT_QUESTIONS