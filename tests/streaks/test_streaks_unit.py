# UNIT TEST FOR QNA
import pytest
from datetime import timedelta
from unittest.mock import Mock, MagicMock

from src.utils.time import get_datetime_now_jkt

from .utils import (
    owner_id,
    streak_obj,
    streak_obj_first_update_after_12h,
    streak_obj_second_update_after_30h,
    streak_obj_terminate_streak_after_30h,
    new_streak_obj_after_30h,
    time_after_12h,
    time_after_30h,
)


# Determine streak decision
def test_determine_streak_decision_continue(streaks_service):
    time_now = get_datetime_now_jkt()

    input_value = {
        "current_time": time_now,
        "streak_last_updated": time_now - timedelta(hours=6),  # still within 24h
    }

    expected_response = "CONTINUE"

    actual_response = streaks_service.determine_streak_decision(**input_value)

    assert actual_response == expected_response


def test_determine_streak_decision_terminate(streaks_service):
    time_now = get_datetime_now_jkt()

    input_value = {
        "current_time": time_now,
        "streak_last_updated": time_now - timedelta(hours=25),  # outside of 24h
    }

    expected_response = "TERMINATE"

    actual_response = streaks_service.determine_streak_decision(**input_value)

    assert actual_response == expected_response


# Update streak length
def test_update_streak_length_after_12h(streaks_service):
    input_value = {
        "streak": streak_obj,
        "time_updated": time_after_12h,
    }

    expected_response = streak_obj_first_update_after_12h

    actual_response = streaks_service.update_streak_length(**input_value)

    assert actual_response == expected_response


# For streak_obj_updated_after_12h, update after 18h
def test_update_streak_12h_by_18h(streaks_service):
    input_value = {
        "streak": streak_obj_first_update_after_12h,
        "time_updated": time_after_30h,
    }

    expected_response = streak_obj_second_update_after_30h

    actual_response = streaks_service.update_streak_length(**input_value)

    assert actual_response == expected_response
