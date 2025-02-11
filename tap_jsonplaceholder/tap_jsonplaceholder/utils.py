"""Utility functions for tap-jsonplaceholder."""
from typing import Dict, Any
from singer_sdk.exceptions import InvalidData
from tap_jsonplaceholder.errors import InvalidRecordError

def validate_record(record: Dict[str, Any], required_fields: list) -> bool:
    """Validate record has all required fields."""
    try:
        for field in required_fields:
            if field not in record:
                raise InvalidRecordError(f"Missing required field: {field}")
            if record[field] is None:
                raise InvalidRecordError(f"Required field {field} cannot be null")
        return True
    except InvalidRecordError as e:
        raise InvalidData(str(e))

def is_valid_post_id(post_id: int) -> bool:
    """Check if post ID is valid (even number)."""
    return isinstance(post_id, int) and post_id % 2 == 0