import json
import re
from typing import Any

def extract_json_from_text(text: str) -> dict[str, Any]:
    """
    Extracts and parses JSON from a string that might contain markdown fences 
    (```json ... ```) or leading/trailing text.
    """
    text = text.strip()
    
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # Look for markdown code block
    json_pattern = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
    match = json_pattern.search(text)
    
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as e:
            raise ValueError(f"Found JSON block but failed to parse: {e}")
            
    # Try to find anything between { and }
    bracket_pattern = re.compile(r"(\{.*\})", re.DOTALL)
    match = bracket_pattern.search(text)
    
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as e:
            raise ValueError(f"Found JSON-like structure but failed to parse: {e}")

    raise ValueError("Could not extract JSON from the provided text.")
