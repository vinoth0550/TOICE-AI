


# phase 2   16/03/2026 ofz

# concurrency_limit.py


import asyncio


# For log errors and terminal log track

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("TASK-PRD-API")

# Allow only 5 concurrent AI executions

CONCURRENCY_LIMIT = 5

semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

