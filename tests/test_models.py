import pytest
from pydantic import ValidationError
from backend.models import ActionItem, MeetingAnalysis

def test_action_item_normalizes_optional_fields() -> None:
    item = ActionItem(task=" Send proposal ", owner="  ", deadline=" Friday ")
    assert item.task == "Send proposal"
    assert item.owner is None
    assert item.deadline == "Friday"

def test_action_item_requires_task() -> None:
    with pytest.raises(ValidationError): ActionItem(task="   ")

def test_meeting_analysis_requires_summary() -> None:
    with pytest.raises(ValidationError): MeetingAnalysis(summary="", key_decisions=[], action_items=[])
