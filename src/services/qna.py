import uuid
from typing import List, Optional

from fastapi import (
  Request,
)
from sqlalchemy.orm import Session
from bson.objectid import ObjectId

from langchain_openai import (
  ChatOpenAI,
  OpenAIEmbeddings
)
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.retrieval_qa.base import (
  BaseRetrievalQA,
  RetrievalQA,
)
from langchain.chains.summarize import load_summarize_chain

from src.models.users import User
from src.schemas.note import (
  NoteSchema
)

from src.schemas.qna import (
  QNAAnswerSchema,
  QNAQuestionSchema,
  QNAQuestionSetSchema,
  QNAQuestionReviewSchema,
  QNASetReviewSchema,
  QNAUserAnswerPayloadSchema,
  QNASetReviewPayloadSchema,
)

from src.utils.settings import (
  OPENAI_MODEL_NAME,
  OPENAI_API_KEY,
)

from src.utils.time import get_datetime_now_jkt

class QNAService:
  MODEL_TEMPERATURE_QUESTION = 0.6
  MODEL_TEMPERATURE_ANSWER = 0.3

  def generate_qna_set(
    self, 
    note: NoteSchema,
    question_count: int,
  ) -> dict:
    # PREPARE LANGUAGE MODELS
    LLM_QUESTION_GEN = ChatOpenAI(
      temperature=self.MODEL_TEMPERATURE_QUESTION, 
      model=OPENAI_MODEL_NAME, 
      api_key=OPENAI_API_KEY,
    )

    LLM_ANSWER_GEN = ChatOpenAI(
      temperature=self.MODEL_TEMPERATURE_ANSWER, 
      model=OPENAI_MODEL_NAME, 
      api_key=OPENAI_API_KEY,
    )

    # DATA PREPROCESSING AND PERSISTENCE
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
        "k": 5,
      },
    )

    # QUESTION GENERATION
    Q_BASE_PROMPT = self.get_q_base_prompt(question_count=question_count)
    Q_REFINED_PROMPT = self.get_q_refined_prompt(question_count=question_count)

    question_gen_chain = load_summarize_chain(
      llm=LLM_QUESTION_GEN,
      chain_type="refine",
      verbose=True,
      question_prompt=Q_BASE_PROMPT,
      refine_prompt=Q_REFINED_PROMPT,
    )

    generated_questions = question_gen_chain.run(note_documents_chunk)

    question_list = generated_questions.split("\n")


    # ANSWER GENERATION
    ANS_GEN_PROMPT = self.get_ans_prompt()

    answer_gen_chain = RetrievalQA.from_chain_type(
      llm=LLM_ANSWER_GEN,
      chain_type="stuff",
      retriever=retriever,
      chain_type_kwargs={
        "prompt": ANS_GEN_PROMPT,
      }
    )

    # Run answer chain for each question
    result = {}

    for q_id in range(len(question_list)):
      question = question_list[q_id]
      answers = []

      for cnt in range(5):
        if len(answers) >= 4:
          break
        
        if cnt > 0:
          # If not the first iteration, then previous iteration resulted in < 4 answers
          print("Answer array has less than 4 items!")
        
        answers = self.generate_answers_for_question(
          answer_gen_chain=answer_gen_chain,
          question=question,
        )

      # Append to Result Dict
      result[str(q_id)] = {
        "question": question,
        # First line = correct answer, the rest = incorrect answers
        "answer_correct": answers[0],
        "answers_incorrect": answers[1:],
      }

      # Print values
      print(result[str(q_id)])
      print("--------------------------------------------------\n\n")

    return result

  def fetch_qna_set_from_note(
    self,
    note_id: str,
    request: Request,
    user: User,
  ) -> QNAQuestionSetSchema | None:
    if user is None:
      return None
    
    my_qna_set = request.app.qna_collection.find_one({
      "note_id": note_id,
      "owner_id": user.id,
    })

    return my_qna_set

  def create_qna_set_obj(
    self, 
    note_id: str,
    question_count: int,
    qna_set: dict,
    user: User,
  ) -> QNAQuestionSetSchema:
    # Create QNA Set variables
    qna_set_uuid = uuid.uuid4()
    datetime_now_jkt = get_datetime_now_jkt()
    PER_QUESTION_SCORE = round(100 / question_count, 3) # Score in { 33.333 | 20.000 | 10.000 }

    qna_set_questions_list: Optional[List[QNAQuestionSchema]] = []

    for q_id in range(question_count):
      qna_pair = qna_set[str(q_id)]

      question: str = qna_pair["question"]
      ans_correct: str = qna_pair["answer_correct"]
      ans_incorrect: List[str] = qna_pair["answers_incorrect"]

      # Generate question-specific constants
      question_id = uuid.uuid4()

      question_answer_key: Optional[QNAAnswerSchema] = None
      question_answers_list: Optional[List[QNAAnswerSchema]] = []

      # Create all Answer schemas for each answer option, convert ans_correct to list first
      options_list = [ans_correct] + ans_incorrect
      for option in options_list:
        is_correct_answer = False

        if option == ans_correct:
          is_correct_answer = True

        qna_answer_obj = QNAAnswerSchema(
          id=uuid.uuid4(),
          question_id=question_id,

          created_at=datetime_now_jkt,
          updated_at=datetime_now_jkt,
          is_deleted=False,

          content=option,
          is_correct_answer=is_correct_answer,
        )

        if is_correct_answer:
          question_answer_key = qna_answer_obj

        # Truncate to 4 answers only - avoid 
        if len(question_answers_list) < 4:
          question_answers_list.append(qna_answer_obj)

      # Create Question object
      qna_question_obj = QNAQuestionSchema(
        id=question_id,
        qna_set_uuid=qna_set_uuid,

        created_at=datetime_now_jkt,
        updated_at=datetime_now_jkt,
        is_deleted=False,

        question=question,
        answer_options=question_answers_list,
        answer_key=question_answer_key,

        question_score=PER_QUESTION_SCORE,
        marked_irrelevant=False,
      )

      qna_set_questions_list.append(qna_question_obj)

    qna_set_obj = QNAQuestionSetSchema(
      uuid=qna_set_uuid,
      owner_id=user.id,
      note_id=note_id,

      created_at=datetime_now_jkt,
      updated_at=datetime_now_jkt,
      is_deleted=False,

      question_count=question_count,
      questions=qna_set_questions_list,
    )

    return qna_set_obj


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

  def generate_answers_for_question(
      self, 
      answer_gen_chain: BaseRetrievalQA,
      question: str,
  ) -> List[str]:
    answers = answer_gen_chain.run(question)
    answers = [line.strip() for line in answers.split("\n")]

    return answers

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

    response_text = f"This is a Cornell-notetaking based Note.\n Note main content:\n{main_f}\n\nNote cues:\n{cues_f}\n\nNote summary: {summary_f}"

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
  def get_q_base_prompt(self, question_count: int):
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
    Please ensure both questions and answers are kept short, no more than 15-20 WORDS!

    QUESTIONS:
    """

    print(prompt_template)

    PROMPT_QUESTIONS = PromptTemplate(
      template=prompt_template, 
      input_variables=["text"]
    )

    return PROMPT_QUESTIONS
  
  def get_q_refined_prompt(self, question_count: int):
    refined_prompt = """
    You are an expert at creating practice questions based on lecture notes.
    Your goal is to help a student prepare for their test.
    You have received some draft questions:

    {existing_answer}
    
    Given the new context below, refine the original questions in English.
    If the context is not helpful, please provide the original questions.
    ------------
    {text}
    ------------
    """

    refined_prompt += f"""
    IMPORTANT COMMANDS:
    First, create {question_count} AND ONLY {question_count} questions only.
    Second, please omit any numbering (e.g. 1.) from both question and answer strings. Return only the text content.
    Third, please ensure questions are kept short, each no more than 15 WORDS!
  
    QUESTIONS:
    """

    REFINE_PROMPT_QUESTIONS = PromptTemplate(
      input_variables=["existing_answer", "text"],
      template=refined_prompt,
    )

    return REFINE_PROMPT_QUESTIONS
  
  def get_ans_prompt(self) -> PromptTemplate:
    ANS_GEN_TEMPLATE = """
    For EACH question, please generate EXACTLY FOUR (4) answer options.
    
    The FIRST output line should be the CORRECT answer to the question, and the NEXT THREE LINES must be an incorrect answer. 
    
    On each line, ONLY OUTPUT THE OPTION TEXT, DO NOT output anything else (such as numbers). 

    Example of a valid output:

    Airtime on Radio East has been secured
    Designer has created new stands
    Looking at providing free gifts at exhibitions
    Publicity material is listed in the annual catalog

    We can interpret this as "Airtime on Radio East has been secured" as the correct answer for the question. The subsequent three lines are the incorrect answers.

    ======

    QUESTIONS:
    {question}
    
    =====
    CONTEXT:
    {context}
    """

    ANS_GEN_PROMPT = PromptTemplate(
      template=ANS_GEN_TEMPLATE,
      input_variables=["context", "question"],
    )

    return ANS_GEN_PROMPT

  def review_qna(
      self,
      request: Request,
      payload: QNASetReviewPayloadSchema,
  ):

    review_qna_set_id = payload.id
    review_owner_id = payload.owner_id
    review_note_id = payload.note_id
    review_created_at = payload.created_at
    review_user_answers = payload.answers

    original_qna_set = request.app.qna_collection.find_one({
      "note_id": review_note_id,
      "owner_id": review_owner_id,
    })

    original_questions = original_qna_set["questions"]

    answered_q: List[QNAQuestionReviewSchema] = [] 
    total_score = 0

    for i, answer in enumerate(review_user_answers):

      review_question_id = answer.question_id
      review_user_answer = answer.answer_id
      review_answer_content = answer.content
      review_user_answer_created_at = answer.created_at


      for question in original_questions:
        if question["id"] != review_question_id:
          continue

        answer_key = question["answer_key"]
        if answer_key["id"] == review_user_answer:

          new_user_answer_object = QNAAnswerSchema(
            id=uuid.uuid4(),
            created_at=review_user_answer_created_at,
            updated_at=review_user_answer_created_at,
            is_deleted=False,
            question_id=review_question_id,
            content=review_answer_content,
            is_correct_answer=True
          )

          new_question_review_object = QNAQuestionReviewSchema(
            id=uuid.uuid4(),
            qna_set_review_uuid=review_qna_set_id,
            created_at=review_user_answer_created_at,
            updated_at=review_user_answer_created_at,
            is_deleted=False,
            question=question["question"],
            question_id=review_question_id,
            user_answer=new_user_answer_object,
            answer_options=question["answer_options"],
            is_answered_correctly=True,
            score_obtained=question["question_score"]
          )

          answered_q.append(new_question_review_object)
          total_score += question["question_score"]
        else:
          new_user_answer_object = QNAAnswerSchema(
            id=uuid.uuid4(),
            created_at=review_user_answer_created_at,
            updated_at=review_user_answer_created_at,
            is_deleted=False,
            question_id=review_question_id,
            content=review_answer_content,
            is_correct_answer=False
          )

          new_question_review_object = QNAQuestionReviewSchema(
            id=uuid.uuid4(),
            qna_set_review_uuid=review_qna_set_id,
            created_at=review_user_answer_created_at,
            updated_at=review_user_answer_created_at,
            is_deleted=False,
            question=question["question"],
            question_id=review_question_id,
            user_answer=new_user_answer_object,
            answer_options=question["answer_options"],
            is_answered_correctly=False,
            score_obtained=0
          )

          answered_q.append(new_question_review_object)

    new_qna_set_review_object = QNASetReviewSchema(
      uuid=uuid.uuid4(),
      note_id=review_note_id,
      owner_id=review_owner_id,
      created_at=review_created_at,
      updated_at=review_created_at,
      is_deleted=False,
      qna_set_id=review_qna_set_id,
      answered_q=answered_q,
      score_obtained=total_score
    )

    return new_qna_set_review_object

  def fetch_qna_review_result_from_mongodb(
    self, 
    note_id: str, 
    request: Request, 
    user: User,
  ) -> NoteSchema:
    qna_review_result = request.app.qna_results_collection.find_one({
      "note_id": note_id,
      "owner_id": user.id,
      "is_deleted": False
    })
    
    return qna_review_result
