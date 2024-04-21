from typing import List
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

from src.utils.settings import (
  OPENAI_MODEL_NAME,
  OPENAI_API_KEY,
)

class QNAService:
  MODEL_TEMPERATURE_QUESTION = 0.6
  MODEL_TEMPERATURE_ANSWER = 0.3

  def generate_qna_set(
    self, 
    note: NoteSchema,
    question_count: int,
    user: User,
  ):
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