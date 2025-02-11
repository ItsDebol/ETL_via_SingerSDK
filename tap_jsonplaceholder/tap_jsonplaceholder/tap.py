"""JSONPlaceholder tap class."""

from typing import List
from singer_sdk import Tap, Stream
from singer_sdk.typing import (
    ArrayType,
    DateTimeType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
    IntegerType,
)

from tap_jsonplaceholder.streams import (
    UsersStream,
    PostsStream,
    CommentsStream,
)

STREAM_TYPES = [
    UsersStream,
    PostsStream,
    CommentsStream,
]


class TapJSONPlaceholder(Tap):
    """JSONPlaceholder tap class."""
    name = "tap-jsonplaceholder"

    config_jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "api_url": {
                "type": "string",
                "default": "https://jsonplaceholder.typicode.com"
            }
        }
    }

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapJSONPlaceholder.cli()