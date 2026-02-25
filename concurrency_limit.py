

# concurrency_limit.py


import asyncio

# Allow only 10 concurrent AI executions
CONCURRENCY_LIMIT = 10

semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)