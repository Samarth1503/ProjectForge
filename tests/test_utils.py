import pytest
from projectforge.utils import extract_json_from_text

def test_extract_json_direct():
    text = '{"key": "value"}'
    assert extract_json_from_text(text) == {"key": "value"}

def test_extract_json_markdown():
    text = '''
    Here is the output you requested:
    ```json
    {
        "key": "value2"
    }
    ```
    Have a nice day!
    '''
    assert extract_json_from_text(text) == {"key": "value2"}

def test_extract_json_markdown_no_lang():
    text = '''
    ```
    {"key": "value3"}
    ```
    '''
    assert extract_json_from_text(text) == {"key": "value3"}

def test_extract_json_brackets_fallback():
    text = '''
    Some preamble text.
    {
        "key": "value4"
    }
    Some postamble text.
    '''
    assert extract_json_from_text(text) == {"key": "value4"}

def test_extract_json_invalid():
    with pytest.raises(ValueError, match="Could not extract JSON"):
        extract_json_from_text("This has no JSON.")

def test_extract_json_malformed():
    text = '''
    ```json
    {"key": "value", } 
    ```
    '''
    # Python's json doesn't allow trailing commas.
    with pytest.raises(ValueError, match="Found JSON block but failed to parse"):
        extract_json_from_text(text)
