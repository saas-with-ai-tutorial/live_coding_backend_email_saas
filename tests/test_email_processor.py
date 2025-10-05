"""
Unit tests for EmailProcessor class.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

import sys
import os
# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.email_processor import EmailProcessor, ActionItem, EmailSummary


class TestActionItemModel:
    """Tests for ActionItem Pydantic model."""
    
    def test_action_item_creation_full(self):
        """Test creating ActionItem with all fields."""
        action_item = ActionItem(
            is_action_item=True,
            action_item="Complete the report",
            due_date="2024-01-20",
            priority="high"
        )
        
        assert action_item.is_action_item is True
        assert action_item.action_item == "Complete the report"
        assert action_item.due_date == "2024-01-20"
        assert action_item.priority == "high"
    
    def test_action_item_creation_minimal(self):
        """Test creating ActionItem with minimal fields."""
        action_item = ActionItem(is_action_item=False)
        
        assert action_item.is_action_item is False
        assert action_item.action_item is None
        assert action_item.due_date is None
        assert action_item.priority is None
    
    def test_action_item_to_dict(self):
        """Test converting ActionItem to dictionary."""
        action_item = ActionItem(
            is_action_item=True,
            action_item="Test action",
            due_date="2024-01-20",
            priority="medium"
        )
        
        result = action_item.model_dump()
        
        assert isinstance(result, dict)
        assert result["is_action_item"] is True
        assert result["action_item"] == "Test action"


class TestEmailSummaryModel:
    """Tests for EmailSummary Pydantic model."""
    
    def test_email_summary_creation(self):
        """Test creating EmailSummary with all fields."""
        summary = EmailSummary(
            summary="This is a test summary",
            key_points=["Point 1", "Point 2"],
            sentiment="positive"
        )
        
        assert summary.summary == "This is a test summary"
        assert len(summary.key_points) == 2
        assert summary.sentiment == "positive"
    
    def test_email_summary_without_sentiment(self):
        """Test creating EmailSummary without sentiment."""
        summary = EmailSummary(
            summary="Test summary",
            key_points=["Point 1"]
        )
        
        assert summary.summary == "Test summary"
        assert summary.sentiment is None


class TestEmailProcessorInitialization:
    """Tests for EmailProcessor initialization."""
    
    def test_initialization_default(self, mock_api_key):
        """Test default initialization with API key from env."""
        processor = EmailProcessor()
        
        assert processor.model == "openai/gpt-4o-mini"
        assert processor.api_key == "test-api-key-12345"
    
    def test_initialization_custom_model(self, mock_api_key):
        """Test initialization with custom model."""
        processor = EmailProcessor(model="openai/gpt-4")
        
        assert processor.model == "openai/gpt-4"
    
    def test_initialization_custom_api_key(self):
        """Test initialization with custom API key."""
        processor = EmailProcessor(api_key="custom-key")
        
        assert processor.api_key == "custom-key"
    
    def test_initialization_no_api_key_warning(self, monkeypatch, capsys):
        """Test warning when no API key is provided."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        processor = EmailProcessor()
        
        captured = capsys.readouterr()
        assert "Warning" in captured.out or processor.api_key is None


class TestEmailProcessorFormatEmail:
    """Tests for _format_email method."""
    
    def test_format_email_complete(self, sample_email_data):
        """Test formatting email with all fields."""
        processor = EmailProcessor(api_key="test-key")
        formatted = processor._format_email(sample_email_data)
        
        assert "Subject: Urgent: Project Review Meeting Tomorrow" in formatted
        assert "From: John Doe <john.doe@example.com>" in formatted
        assert "To: jane.doe@example.com" in formatted
        assert "Body:" in formatted
        assert "project review meeting" in formatted
    
    def test_format_email_no_from_name(self):
        """Test formatting email without from_name."""
        processor = EmailProcessor(api_key="test-key")
        email_data = {
            "subject": "Test",
            "from": "test@example.com",
            "from_name": "",
            "to": "recipient@example.com",
            "date": "2024-01-15",
            "body": "Test body"
        }
        
        formatted = processor._format_email(email_data)
        
        assert "From: test@example.com" in formatted
        assert "From:  <test@example.com>" not in formatted
    
    def test_format_email_missing_fields(self):
        """Test formatting email with missing optional fields."""
        processor = EmailProcessor(api_key="test-key")
        email_data = {"body": "Just a body"}
        
        formatted = processor._format_email(email_data)
        
        assert "Subject: No Subject" in formatted
        assert "From: Unknown" in formatted
        assert "Just a body" in formatted


class TestEmailProcessorExtractActionItem:
    """Tests for extract_action_item method."""
    
    @patch('src.core.email_processor.completion')
    def test_extract_action_item_success(self, mock_completion, sample_email_data, mock_llm_response_action_item):
        """Test successful action item extraction."""
        # Setup mock
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_llm_response_action_item)
        mock_completion.return_value = mock_response
        
        processor = EmailProcessor(api_key="test-key")
        result = processor.extract_action_item(sample_email_data)
        
        assert isinstance(result, ActionItem)
        assert result.is_action_item is True
        assert result.action_item is not None
        assert result.priority == "high"
        
        # Verify completion was called with correct parameters
        mock_completion.assert_called_once()
        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs["model"] == "openai/gpt-4o-mini"
        assert call_kwargs["response_format"] == ActionItem
    
    @patch('src.core.email_processor.completion')
    def test_extract_action_item_no_action(self, mock_completion, non_action_email_data, mock_llm_response_no_action):
        """Test extraction when email has no action item."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_llm_response_no_action)
        mock_completion.return_value = mock_response
        
        processor = EmailProcessor(api_key="test-key")
        result = processor.extract_action_item(non_action_email_data)
        
        assert isinstance(result, ActionItem)
        assert result.is_action_item is False
        assert result.action_item is None
    
    @patch('src.core.email_processor.completion')
    def test_extract_action_item_error_handling(self, mock_completion, sample_email_data):
        """Test error handling when LLM call fails."""
        mock_completion.side_effect = Exception("API Error")
        
        processor = EmailProcessor(api_key="test-key")
        result = processor.extract_action_item(sample_email_data)
        
        # Should return empty action item on error
        assert isinstance(result, ActionItem)
        assert result.is_action_item is False
    
    @patch('src.core.email_processor.completion')
    def test_extract_action_item_dict_response(self, mock_completion, sample_email_data, mock_llm_response_action_item):
        """Test handling dict response (not JSON string)."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_llm_response_action_item  # Dict instead of JSON string
        mock_completion.return_value = mock_response
        
        processor = EmailProcessor(api_key="test-key")
        result = processor.extract_action_item(sample_email_data)
        
        assert isinstance(result, ActionItem)
        assert result.is_action_item is True


class TestEmailProcessorSummarizeEmail:
    """Tests for summarize_email method."""
    
    @patch('src.core.email_processor.completion')
    def test_summarize_email_success(self, mock_completion, sample_email_data, mock_llm_response_summary):
        """Test successful email summarization."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_llm_response_summary)
        mock_completion.return_value = mock_response
        
        processor = EmailProcessor(api_key="test-key")
        result = processor.summarize_email(sample_email_data)
        
        assert isinstance(result, EmailSummary)
        assert len(result.summary) > 0
        assert len(result.key_points) > 0
        assert result.sentiment in ["positive", "neutral", "negative"]
    
    @patch('src.core.email_processor.completion')
    def test_summarize_email_error_handling(self, mock_completion, sample_email_data):
        """Test error handling when summarization fails."""
        mock_completion.side_effect = Exception("API Error")
        
        processor = EmailProcessor(api_key="test-key")
        result = processor.summarize_email(sample_email_data)
        
        # Should return error summary
        assert isinstance(result, EmailSummary)
        assert "Error processing email" in result.summary
        assert result.sentiment == "neutral"


class TestEmailProcessorCategorizeEmail:
    """Tests for categorize_email method."""
    
    @patch('src.core.email_processor.completion')
    def test_categorize_email_success(self, mock_completion, sample_email_data):
        """Test successful email categorization."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Work/Business"
        mock_completion.return_value = mock_response
        
        processor = EmailProcessor(api_key="test-key")
        result = processor.categorize_email(sample_email_data)
        
        assert isinstance(result, str)
        assert result == "Work/Business"
    
    @patch('src.core.email_processor.completion')
    def test_categorize_email_with_whitespace(self, mock_completion, sample_email_data):
        """Test categorization with whitespace in response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "  Personal  \n"
        mock_completion.return_value = mock_response
        
        processor = EmailProcessor(api_key="test-key")
        result = processor.categorize_email(sample_email_data)
        
        assert result == "Personal"
    
    @patch('src.core.email_processor.completion')
    def test_categorize_email_error_handling(self, mock_completion, sample_email_data):
        """Test error handling when categorization fails."""
        mock_completion.side_effect = Exception("API Error")
        
        processor = EmailProcessor(api_key="test-key")
        result = processor.categorize_email(sample_email_data)
        
        assert result == "Other"


class TestEmailProcessorBatchOperations:
    """Tests for batch processing methods."""
    
    @patch('src.core.email_processor.completion')
    def test_process_email_batch_all_operations(self, mock_completion, batch_email_data, 
                                                mock_llm_response_action_item,
                                                mock_llm_response_summary):
        """Test batch processing with all operations enabled."""
        # Setup mock to return different responses
        mock_responses = []
        
        # For each email, we need: action_item, summary, category
        for _ in batch_email_data:
            # Action item response
            resp1 = Mock()
            resp1.choices = [Mock()]
            resp1.choices[0].message.content = json.dumps(mock_llm_response_action_item)
            mock_responses.append(resp1)
            
            # Summary response
            resp2 = Mock()
            resp2.choices = [Mock()]
            resp2.choices[0].message.content = json.dumps(mock_llm_response_summary)
            mock_responses.append(resp2)
            
            # Category response
            resp3 = Mock()
            resp3.choices = [Mock()]
            resp3.choices[0].message.content = "Work/Business"
            mock_responses.append(resp3)
        
        mock_completion.side_effect = mock_responses
        
        processor = EmailProcessor(api_key="test-key")
        results = processor.process_email_batch(
            batch_email_data,
            extract_actions=True,
            summarize=True,
            categorize=True
        )
        
        assert len(results) == 3
        for result in results:
            assert "action_item" in result
            assert "summary" in result
            assert "category" in result
    
    @patch('src.core.email_processor.completion')
    def test_process_email_batch_actions_only(self, mock_completion, batch_email_data, 
                                               mock_llm_response_action_item):
        """Test batch processing with only action extraction."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_llm_response_action_item)
        mock_completion.return_value = mock_response
        
        processor = EmailProcessor(api_key="test-key")
        results = processor.process_email_batch(
            batch_email_data,
            extract_actions=True,
            summarize=False,
            categorize=False
        )
        
        assert len(results) == 3
        for result in results:
            assert "action_item" in result
            assert "summary" not in result
            assert "category" not in result
    
    @patch('src.core.email_processor.completion')
    def test_process_email_batch_with_errors(self, mock_completion, batch_email_data,
                                             mock_llm_response_action_item):
        """Test batch processing continues after individual errors."""
        # First call succeeds, second fails, third succeeds
        responses = [
            Mock(choices=[Mock(message=Mock(content=json.dumps(mock_llm_response_action_item)))]),
            Exception("API Error"),
            Mock(choices=[Mock(message=Mock(content=json.dumps(mock_llm_response_action_item)))])
        ]
        mock_completion.side_effect = responses
        
        processor = EmailProcessor(api_key="test-key")
        results = processor.process_email_batch(
            batch_email_data,
            extract_actions=True
        )
        
        # All emails should be in results, even if some failed
        assert len(results) == 3
    
    @patch('src.core.email_processor.completion')
    def test_extract_action_items_from_batch(self, mock_completion, batch_email_data):
        """Test extracting only emails with action items."""
        # Setup: first email has action, second doesn't, third has action
        responses = [
            Mock(choices=[Mock(message=Mock(content=json.dumps({
                "is_action_item": True,
                "action_item": "Do something",
                "due_date": "Tomorrow",
                "priority": "high"
            })))]),
            Mock(choices=[Mock(message=Mock(content=json.dumps({
                "is_action_item": False,
                "action_item": None,
                "due_date": None,
                "priority": None
            })))]),
            Mock(choices=[Mock(message=Mock(content=json.dumps({
                "is_action_item": True,
                "action_item": "Submit report",
                "due_date": "Friday",
                "priority": "medium"
            })))])
        ]
        mock_completion.side_effect = responses
        
        processor = EmailProcessor(api_key="test-key")
        action_emails = processor.extract_action_items_from_batch(batch_email_data)
        
        # Should only return emails with action items
        assert len(action_emails) == 2
        for email in action_emails:
            assert "action_item" in email
            assert email["action_item"]["is_action_item"] is True


class TestEmailProcessorSystemPrompts:
    """Tests for system prompts."""
    
    def test_action_item_prompt_exists(self):
        """Test that ACTION_ITEM_PROMPT is defined."""
        assert hasattr(EmailProcessor, 'ACTION_ITEM_PROMPT')
        assert len(EmailProcessor.ACTION_ITEM_PROMPT) > 0
        assert "action item" in EmailProcessor.ACTION_ITEM_PROMPT.lower()
    
    def test_summary_prompt_exists(self):
        """Test that SUMMARY_PROMPT is defined."""
        assert hasattr(EmailProcessor, 'SUMMARY_PROMPT')
        assert len(EmailProcessor.SUMMARY_PROMPT) > 0
        assert "summary" in EmailProcessor.SUMMARY_PROMPT.lower()
    
    def test_category_prompt_exists(self):
        """Test that CATEGORY_PROMPT is defined."""
        assert hasattr(EmailProcessor, 'CATEGORY_PROMPT')
        assert len(EmailProcessor.CATEGORY_PROMPT) > 0
        assert "categorize" in EmailProcessor.CATEGORY_PROMPT.lower()


class TestEmailProcessorIntegration:
    """Integration tests with actual email data."""
    
    @patch('src.core.email_processor.completion')
    def test_full_email_processing_workflow(self, mock_completion, sample_email_data):
        """Test complete workflow from email to processed results."""
        # Setup mock for multiple calls
        mock_responses = [
            # Action item extraction
            Mock(choices=[Mock(message=Mock(content=json.dumps({
                "is_action_item": True,
                "action_item": "Prepare and attend meeting",
                "due_date": "Tomorrow 2 PM",
                "priority": "high"
            })))]),
            # Email summary
            Mock(choices=[Mock(message=Mock(content=json.dumps({
                "summary": "Meeting request with preparation items",
                "key_points": ["Meeting tomorrow", "Prepare reports"],
                "sentiment": "neutral"
            })))]),
            # Categorization
            Mock(choices=[Mock(message=Mock(content="Work/Business"))])
        ]
        mock_completion.side_effect = mock_responses
        
        processor = EmailProcessor(api_key="test-key")
        
        # Test individual operations
        action_item = processor.extract_action_item(sample_email_data)
        assert action_item.is_action_item is True
        
        summary = processor.summarize_email(sample_email_data)
        assert len(summary.key_points) > 0
        
        category = processor.categorize_email(sample_email_data)
        assert category == "Work/Business"


# Run tests with coverage if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.core.email_processor", "--cov-report=term-missing"])
