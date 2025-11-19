"""
Intent Parser Tests
~~~~~~~~~~~~~~~~~~~

Tests for natural language intent parsing.
"""

import pytest
from app.agents.intent_parser import IntentParser, Intent


def test_check_completion_intent():
    """Test completion check intent"""
    query = "Did I complete my training?"
    intent = IntentParser.classify_intent(query)
    assert intent == Intent.CHECK_COMPLETION


def test_missing_videos_intent():
    """Test missing videos intent"""
    query = "Which videos am I missing?"
    intent = IntentParser.classify_intent(query)
    assert intent == Intent.LIST_MISSING_VIDEOS


def test_completed_videos_intent():
    """Test completed videos intent"""
    query = "What videos have I finished?"
    intent = IntentParser.classify_intent(query)
    assert intent == Intent.LIST_COMPLETED_VIDEOS


def test_video_duration_intent():
    """Test video duration intent"""
    query = "How long did video 3 take me?"
    intent = IntentParser.classify_intent(query)
    assert intent == Intent.VIDEO_DURATION


def test_extract_video_number():
    """Test video number extraction"""
    query = "Show me video 3 details"
    video_num = IntentParser.extract_video_number(query)
    assert video_num == 3


def test_extract_status():
    """Test status extraction"""
    query = "Show employees who have finished"
    status = IntentParser.extract_status(query)
    assert status == "FINISHED"


def test_is_ciso_query():
    """Test CISO query detection"""
    query = "Show me all employees' training status"
    is_ciso = IntentParser.is_ciso_query(query)
    assert is_ciso is True


def test_is_not_ciso_query():
    """Test non-CISO query detection"""
    query = "What is my training status?"
    is_ciso = IntentParser.is_ciso_query(query)
    assert is_ciso is False


def test_full_parse():
    """Test full query parsing"""
    query = "How long did video 2 take?"
    parsed = IntentParser.parse(query)
    assert parsed["intent"] == Intent.VIDEO_DURATION
    assert parsed["video_number"] == 2
    assert parsed["employee_mention"] == "self"

