

# AI_usage_tracker.py 


# import time
# from database import ai_usage_collection
# from concurrency_limit import logger
# from gemini_service import latency

# # Gemini Flash pricing example

# INPUT_COST_PER_TOKEN = 0.35 / 1_000_000
# OUTPUT_COST_PER_TOKEN = 0.53 / 1_000_000


# def track_ai_usage(endpoint, response, group_id=None, task_id=None):

#     usage = response.usage_metadata

#     if not usage:
#         return

#     prompt_tokens = usage.prompt_token_count
#     completion_tokens = usage.candidates_token_count
#     total_tokens = usage.total_token_count

#     cost = (
#         prompt_tokens * INPUT_COST_PER_TOKEN +
#         completion_tokens * OUTPUT_COST_PER_TOKEN
#     )

#     log_data = {
#         "endpoint": endpoint,
#         "group_id": group_id,
#         "task_id": task_id,
#         "prompt_tokens": prompt_tokens,
#         "completion_tokens": completion_tokens,
#         "total_tokens": total_tokens,
#         "cost": cost,
#         "created_at": time.time(),


#         "latency": latency
#     }

#     ai_usage_collection.insert_one(log_data)

#     logger.info(
#         f"AI_USAGE | endpoint={endpoint} | "
#         f"tokens={total_tokens} | cost=${cost:.6f}"
#         f"cost=${cost:.6f} | "
#         f"latency={latency:.2f}s"

#     )








# import time
# from database import ai_usage_collection
# from concurrency_limit import logger

# INPUT_COST_PER_TOKEN = 0.35 / 1_000_000
# OUTPUT_COST_PER_TOKEN = 0.53 / 1_000_000


# def track_ai_usage(endpoint, response, latency, group_id=None, task_id=None):

#     usage = response.usage_metadata

#     if not usage:
#         return

#     prompt_tokens = usage.prompt_token_count
#     completion_tokens = usage.candidates_token_count
#     total_tokens = usage.total_token_count

#     cost = (
#         prompt_tokens * INPUT_COST_PER_TOKEN +
#         completion_tokens * OUTPUT_COST_PER_TOKEN
#     )

#     log_data = {
#         "endpoint": endpoint,
#         "group_id": group_id,
#         "task_id": task_id,
#         "prompt_tokens": prompt_tokens,
#         "completion_tokens": completion_tokens,
#         "total_tokens": total_tokens,
#         "cost": cost,
#         "latency": latency,
#         "created_at": time.time()
#     }

#     ai_usage_collection.insert_one(log_data)

#     logger.info(
#         f"AI_USAGE | endpoint={endpoint} | "
#         f"tokens={total_tokens} | "
#         f"cost=${cost:.6f} | "
#         f"latency={latency:.2f}s"
#     )






import time
from database import ai_usage_collection
from concurrency_limit import logger

INPUT_COST_PER_TOKEN = 0.35 / 1_000_000
OUTPUT_COST_PER_TOKEN = 0.53 / 1_000_000


def track_ai_usage(endpoint, response, latency, group_id=None, task_id=None):

    try:
        # Safely get usage metadata
        usage = getattr(response, "usage_metadata", None)

        if not usage:
            logger.warning("AI usage metadata missing")
            return

        # Safely read token values (default = 0 if None)
        prompt_tokens = usage.prompt_token_count or 0
        completion_tokens = usage.candidates_token_count or 0
        total_tokens = usage.total_token_count or 0

        # Calculate cost
        cost = (
            prompt_tokens * INPUT_COST_PER_TOKEN +
            completion_tokens * OUTPUT_COST_PER_TOKEN
        )

        log_data = {
            "endpoint": endpoint,
            "group_id": group_id,
            "task_id": task_id,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost": cost,
            "latency": latency,
            "created_at": time.time()
        }

        # Insert log safely
        ai_usage_collection.insert_one(log_data)

        logger.info(
            f"AI_USAGE | endpoint={endpoint} | "
            f"tokens={total_tokens} | "
            f"cost=${cost:.6f} | "
            f"latency={latency:.2f}s"
        )

    except Exception as e:
        # Never break the main API
        logger.error(f"AI usage tracking failed: {str(e)}")