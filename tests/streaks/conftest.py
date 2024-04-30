import pytest
from src.services.streaks import (
  StreaksService
)

@pytest.fixture(scope="session")
def streaks_service():
  """
  Create QnA Service object
  """

  streaks_service = StreaksService()
  return streaks_service

