# Tests

This directory contains the test suite for the Email SaaS backend.

## Structure

```
tests/
├── __init__.py              # Makes tests a package
├── conftest.py              # Pytest fixtures and configuration
├── test_email_processor.py  # Tests for EmailProcessor class
├── test_gmail_helper.py     # Tests for GmailHelper class
└── README.md               # This file
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
# From the backend root directory
pytest

# Or with coverage
pytest --cov=src --cov-report=html
```

### Run Specific Test Files

```bash
# Test EmailProcessor only
pytest tests/test_email_processor.py

# Test GmailHelper only
pytest tests/test_gmail_helper.py
```

### Run Specific Test Classes or Methods

```bash
# Run a specific test class
pytest tests/test_email_processor.py::TestEmailProcessorInitialization

# Run a specific test method
pytest tests/test_email_processor.py::TestEmailProcessorInitialization::test_initialization_default
```

### Run with Verbosity

```bash
# Verbose output
pytest -v

# Very verbose output
pytest -vv

# Show print statements
pytest -s
```

### Run with Coverage Report

```bash
# Terminal coverage report
pytest --cov=src --cov-report=term-missing

# HTML coverage report (opens in browser)
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Both terminal and HTML
pytest --cov=src --cov-report=term-missing --cov-report=html
```

### Run Tests by Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

## Test Coverage

Current test coverage includes:

### EmailProcessor (`test_email_processor.py`)
- ✅ Model validation (ActionItem, EmailSummary)
- ✅ Initialization and configuration
- ✅ Email formatting
- ✅ Action item extraction
- ✅ Email summarization
- ✅ Email categorization
- ✅ Batch processing
- ✅ Error handling
- ✅ Integration workflows

### GmailHelper (`test_gmail_helper.py`)
- ✅ Initialization with credentials
- ✅ Connection management
- ✅ Header decoding
- ✅ Email body extraction
- ✅ Reading emails (all/unread)
- ✅ Marking emails as read/unread
- ✅ Folder management
- ✅ Context manager usage
- ✅ Error handling

## Writing New Tests

### Test Structure

Follow this structure for new test files:

```python
"""
Description of what is being tested.
"""
import pytest
from unittest.mock import Mock, patch

# Test class for logical grouping
class TestFeatureName:
    """Tests for specific feature."""
    
    def test_specific_behavior(self):
        """Test description."""
        # Arrange
        setup_data = {}
        
        # Act
        result = function_to_test(setup_data)
        
        # Assert
        assert result == expected_value
```

### Using Fixtures

Fixtures are defined in `conftest.py` and automatically available in all tests:

```python
def test_with_fixture(self, sample_email_data):
    """Test using predefined fixture."""
    processor = EmailProcessor()
    result = processor.extract_action_item(sample_email_data)
    assert result.is_action_item is True
```

### Mocking External Calls

Use `unittest.mock` to mock external API calls:

```python
@patch('src.core.email_processor.completion')
def test_with_mock(self, mock_completion):
    """Test with mocked LLM call."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"result": "test"}'
    mock_completion.return_value = mock_response
    
    # Your test code here
```

## Continuous Integration

Tests should be run in CI/CD pipeline before deployment:

```bash
# CI test command
pytest --cov=src --cov-report=xml --cov-fail-under=80
```

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
2. **One Assertion Per Test**: Each test should verify one specific behavior
3. **Arrange-Act-Assert**: Follow the AAA pattern for test structure
4. **Use Fixtures**: Reuse common test data through fixtures
5. **Mock External Services**: Never make real API calls in tests
6. **Test Edge Cases**: Include tests for error conditions and edge cases
7. **Keep Tests Fast**: Avoid slow operations; mock I/O operations
8. **Independent Tests**: Tests should not depend on each other

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running pytest from the backend root:

```bash
cd /path/to/backend
pytest
```

### Mock Not Working

Ensure you're patching the correct path (where it's used, not where it's defined):

```python
# Correct: patch where completion is used
@patch('src.core.email_processor.completion')

# Wrong: patch where it's defined
@patch('litellm.completion')
```

### Environment Variables

For tests requiring environment variables, use `monkeypatch` fixture:

```python
def test_with_env(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    # Your test code
```

## Contributing

When adding new features:
1. Write tests first (TDD approach recommended)
2. Ensure all tests pass
3. Maintain or increase code coverage
4. Add relevant fixtures to `conftest.py` if needed
