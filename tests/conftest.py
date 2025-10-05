"""
Pytest configuration and fixtures.
"""
import pytest
import os
from typing import Dict, Any


@pytest.fixture
def sample_email_data() -> Dict[str, Any]:
    """
    Sample email data for testing.
    """
    return {
        "subject": "Urgent: Project Review Meeting Tomorrow",
        "from": "john.doe@example.com",
        "from_name": "John Doe",
        "to": "jane.doe@example.com",
        "date": "2024-01-15 10:30:00",
        "body": """Hi Jane,

I hope this email finds you well. We need to urgently schedule a project review meeting for tomorrow at 2 PM. 

Please prepare the following:
1. Q4 performance metrics
2. Budget analysis report
3. Next quarter roadmap

This is critical for our stakeholder presentation on Friday. Let me know if you can make it.

Best regards,
John"""
    }


@pytest.fixture
def non_action_email_data() -> Dict[str, Any]:
    """
    Sample email without action items.
    """
    return {
        "subject": "Happy Birthday!",
        "from": "friend@example.com",
        "from_name": "Best Friend",
        "to": "you@example.com",
        "date": "2024-01-15 09:00:00",
        "body": """Happy Birthday!

Wishing you all the best on your special day. Hope you have an amazing celebration!

Cheers,
Your Friend"""
    }


@pytest.fixture
def batch_email_data(sample_email_data, non_action_email_data) -> list:
    """
    Batch of emails for testing batch operations.
    """
    return [
        sample_email_data,
        non_action_email_data,
        {
            "subject": "Weekly Report Due This Friday",
            "from": "manager@example.com",
            "from_name": "Manager",
            "to": "team@example.com",
            "date": "2024-01-15 14:00:00",
            "body": "Please submit your weekly reports by Friday EOD. This is important."
        }
    ]


@pytest.fixture
def mock_llm_response_action_item():
    """
    Mock LLM response for action item extraction.
    """
    return {
        "is_action_item": True,
        "action_item": "Schedule and prepare for project review meeting tomorrow at 2 PM with Q4 metrics, budget analysis, and roadmap",
        "due_date": "Tomorrow at 2 PM",
        "priority": "high"
    }


@pytest.fixture
def mock_llm_response_no_action():
    """
    Mock LLM response for non-action email.
    """
    return {
        "is_action_item": False,
        "action_item": None,
        "due_date": None,
        "priority": None
    }


@pytest.fixture
def mock_llm_response_summary():
    """
    Mock LLM response for email summary.
    """
    return {
        "summary": "Meeting request for tomorrow at 2 PM with preparation requirements.",
        "key_points": [
            "Project review meeting tomorrow at 2 PM",
            "Prepare Q4 performance metrics",
            "Prepare budget analysis report",
            "Prepare next quarter roadmap",
            "Related to stakeholder presentation on Friday"
        ],
        "sentiment": "neutral"
    }


@pytest.fixture
def mock_api_key(monkeypatch):
    """
    Set mock API key in environment.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key-12345")
    return "test-api-key-12345"
