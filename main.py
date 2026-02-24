
# main.py

from fastapi import FastAPI
from routers import prd_router, task_router

app = FastAPI()

app.include_router(prd_router.router)
app.include_router(task_router.router)