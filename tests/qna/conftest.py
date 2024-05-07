import pytest
from src.services.qna import (
  QNAService
)

@pytest.fixture(scope="session")
def qna_service():
  """
  Create QnA Service object
  """

  qna_service = QNAService()
  return qna_service

