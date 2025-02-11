from typing import Dict, List
from singer_sdk.exceptions import InvalidData
import statistics

def calculate_metrics(post: Dict, comments: List[Dict]) -> Dict:
    """Calculate post metrics with additional error handling."""
    try:
        if not comments:
            return {
                "comment_count": 0,
                "unique_commenters": 0,
                "total_comment_length": 0,
                "average_comment_length": 0
            }

        comment_lengths = [len(comment["body"]) for comment in comments]
        
        metrics = {
            "comment_count": len(comments),
            "unique_commenters": len(set(comment["email"] for comment in comments)),
            "total_comment_length": sum(comment_lengths),
            "average_comment_length": statistics.mean(comment_lengths),
            "max_comment_length": max(comment_lengths),
            "min_comment_length": min(comment_lengths)
        }

        # Add optional median if there are enough comments
        if len(comments) >= 3:
            metrics["median_comment_length"] = statistics.median(comment_lengths)

        return metrics

    except KeyError as e:
        raise InvalidData(f"Missing required field in comment data: {str(e)}")
    except statistics.StatisticsError as e:
        raise InvalidData(f"Statistical calculation error: {str(e)}")
    except Exception as e:
        raise InvalidData(f"Unexpected error calculating metrics: {str(e)}")