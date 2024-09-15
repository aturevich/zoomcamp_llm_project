import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone


def load_feedback_data():
    feedback_file = Path("feedback.json")
    if feedback_file.exists():
        with feedback_file.open("r") as f:
            return json.load(f)
    return []


def process_feedback_data(feedback_data):
    positive_feedback = sum(1 for feedback in feedback_data if feedback.rating == 1)
    negative_feedback = sum(1 for feedback in feedback_data if feedback.rating == -1)
    total_feedback = positive_feedback + negative_feedback

    return {
        "positive_feedback": positive_feedback,
        "negative_feedback": negative_feedback,
        "total_feedback": total_feedback,
        "positive_percentage": (
            (positive_feedback / total_feedback) * 100 if total_feedback > 0 else 0
        ),
        "negative_percentage": (
            (negative_feedback / total_feedback) * 100 if total_feedback > 0 else 0
        ),
    }


def calculate_response_time_stats(interactions):
    response_times = [
        interaction.response_time
        for interaction in interactions
        if interaction.response_time is not None
    ]

    if not response_times:
        return {
            "average_response_time": 0,
            "min_response_time": 0,
            "max_response_time": 0,
        }

    return {
        "average_response_time": sum(response_times) / len(response_times),
        "min_response_time": min(response_times),
        "max_response_time": max(response_times),
    }


def analyze_query_topics(interactions):
    # This is a simplified version. You might want to implement more sophisticated topic analysis.
    topics = [
        interaction.query.lower().split()[0]
        for interaction in interactions
        if interaction.query
    ]
    topic_counts = Counter(topics)
    return dict(topic_counts.most_common(10))


def aggregate_error_info(interactions):
    errors = [interaction.error for interaction in interactions if interaction.error]
    if not errors:
        return {"No errors": 0}
    error_counts = Counter(errors)
    return dict(error_counts.most_common(10))


def track_system_usage(interactions):
    last_week = datetime.now(timezone.utc) - timedelta(days=7)
    total_queries = 0
    queries_last_week = 0

    for interaction in interactions:
        total_queries += 1
        # Make interaction.timestamp timezone-aware
        if interaction.timestamp.tzinfo is None:
            interaction_timestamp = interaction.timestamp.replace(tzinfo=timezone.utc)
        else:
            interaction_timestamp = interaction.timestamp

        if interaction_timestamp >= last_week:
            queries_last_week += 1

    return {
        "total_queries": total_queries,
        "queries_last_week": queries_last_week,
        "average_queries_per_day": queries_last_week / 7,
    }


def analyze_answer_metrics(interactions):
    total_tokens = 0
    source_types = defaultdict(int)
    interactions_with_metrics = 0

    for interaction in interactions:
        print(f"Interaction ID: {interaction.id}")
        print(f"Retrieval Metrics: {interaction.retrieval_metrics}")
        if interaction.retrieval_metrics:
            try:
                metrics = json.loads(interaction.retrieval_metrics)
                if metrics is not None:
                    tokens = metrics.get("total_tokens", 0)
                    print(f"Tokens: {tokens}")
                    total_tokens += tokens
                    for source in metrics.get("sources", []):
                        source_type = source.get("type", "unknown")
                        source_types[source_type] += 1
                    interactions_with_metrics += 1
                else:
                    print(f"Metrics is None for interaction {interaction.id}")
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for interaction {interaction.id}")
        else:
            print(f"No retrieval metrics for interaction {interaction.id}")

    avg_tokens = (
        total_tokens / interactions_with_metrics if interactions_with_metrics > 0 else 0
    )
    print(f"Total tokens: {total_tokens}")
    print(f"Interactions with metrics: {interactions_with_metrics}")
    print(f"Average tokens: {avg_tokens}")

    return {"average_tokens": round(avg_tokens, 2), "source_types": dict(source_types)}
