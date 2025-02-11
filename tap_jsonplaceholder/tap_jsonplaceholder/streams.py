"""Stream type classes for tap-jsonplaceholder."""

from typing import Any, Dict, Optional, Iterable
from singer_sdk import typing as th
from singer_sdk.streams.rest import RESTStream
from datetime import datetime
from tap_jsonplaceholder.validators import PostValidator, CommentValidator, UserValidator


class JSONPlaceholderStream(RESTStream):
    """JSONPlaceholder stream class."""

    url_base = "https://jsonplaceholder.typicode.com"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "$[*]"

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        return {}

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        return {}


class UsersStream(JSONPlaceholderStream):
    """Users stream."""
    
    # Define class variables
    name = "users"
    path = "/users"
    
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("username", th.StringType),
        th.Property("email", th.StringType),
        th.Property("address", th.ObjectType(
            th.Property("street", th.StringType),
            th.Property("suite", th.StringType),
            th.Property("city", th.StringType),
            th.Property("zipcode", th.StringType),
            th.Property("geo", th.ObjectType(
                th.Property("lat", th.StringType),
                th.Property("lng", th.StringType)
            ))
        )),
        th.Property("phone", th.StringType),
        th.Property("website", th.StringType),
        th.Property("company", th.ObjectType(
            th.Property("name", th.StringType),
            th.Property("catchPhrase", th.StringType),
            th.Property("bs", th.StringType)
        ))
    ).to_dict()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = UserValidator()

    def parse_response(self, response) -> Iterable[dict]:
        """Parse the response and validate records."""
        records = response.json()
        for record in records:
            if not self.validator.validate(record):
                self.logger.warning(
                    f"Validation errors for user {record.get('id')}: {self.validator.errors}"
                )
                record['_metadata'] = {
                    'validation_errors': self.validator.errors.copy(),
                    'validation_timestamp': datetime.utcnow().isoformat()
                }
            yield record


class PostsStream(JSONPlaceholderStream):
    """Posts stream."""
    
    # Define class variables
    name = "posts"
    path = "/posts"
    
    schema = th.PropertiesList(
        th.Property("userId", th.IntegerType),
        th.Property("id", th.IntegerType),
        th.Property("title", th.StringType),
        th.Property("body", th.StringType)
    ).to_dict()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = PostValidator()

    def parse_response(self, response) -> Iterable[dict]:
        """Parse the response and validate records with even IDs."""
        records = response.json()
        for record in records:
            if record['id'] % 2 == 0:
                if not self.validator.validate(record):
                    self.logger.warning(
                        f"Validation errors for post {record.get('id')}: {self.validator.errors}"
                    )
                    record['_metadata'] = {
                        'validation_errors': self.validator.errors.copy(),
                        'validation_timestamp': datetime.utcnow().isoformat()
                    }
                yield record


class CommentsStream(JSONPlaceholderStream):
    """Comments stream."""
    
    # Define class variables
    name = "comments"
    path = "/comments"
    
    schema = th.PropertiesList(
        th.Property("postId", th.IntegerType),
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("email", th.StringType),
        th.Property("body", th.StringType)
    ).to_dict()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = CommentValidator()

    def parse_response(self, response) -> Iterable[dict]:
        """Parse the response and validate records with even postIds."""
        records = response.json()
        for record in records:
            if record['postId'] % 2 == 0:
                if not self.validator.validate(record):
                    self.logger.warning(
                        f"Validation errors for comment {record.get('id')}: {self.validator.errors}"
                    )
                    record['_metadata'] = {
                        'validation_errors': self.validator.errors.copy(),
                        'validation_timestamp': datetime.utcnow().isoformat()
                    }
                yield record


class ValidationStats:
    """Track validation statistics for streams."""
    
    def __init__(self):
        self.total_records = 0
        self.valid_records = 0
        self.invalid_records = 0
        self.error_types = {}

    def update(self, is_valid: bool, errors: list = None):
        """Update validation statistics."""
        self.total_records += 1
        if is_valid:
            self.valid_records += 1
        else:
            self.invalid_records += 1
            if errors:
                for error in errors:
                    self.error_types[error] = self.error_types.get(error, 0) + 1

    def get_summary(self) -> Dict[str, Any]:
        """Get validation statistics summary."""
        return {
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "validity_rate": (self.valid_records / self.total_records * 100 
                            if self.total_records > 0 else 0),
            "error_types": self.error_types
        }