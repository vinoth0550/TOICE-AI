
# task_report_router.py


from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import asyncio

from database import  task_chat_collection, task_collection
from gemini_service import generate_task_report
from concurrency_limit import semaphore

router = APIRouter()


async def safe_run_with_timeout(func, *args, timeout: int = 120):
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(func, *args),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Task report generation timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-task-report")
async def generate_task_report_endpoint(
    
    task_id: str = Form(...)


):

    # STEP 1 — Fetch task PRD
    task_prd = task_collection.find_one(
        {"task_id": task_id},
        {"_id": 0}
    )

    if not task_prd:
        raise HTTPException(status_code=404, detail="Task PRD not found")

    # STEP 2 — Fetch chats sorted ASC
    fetch_chats = task_chat_collection.find(
        {"task_id": task_id}
    ).sort("created_at", 1)

    chats = list(fetch_chats)

    if not chats:
        raise HTTPException(status_code=404, detail="No chats found for this task")

    # Extract only needed chat text
    chat_texts = [
        f"{chat['sender_id']}: {chat['message']}"
        for chat in chats
    ]

    # STEP 3 — Call AI
    async with semaphore:
        ai_response = await safe_run_with_timeout(
            generate_task_report,
            task_prd,
            chat_texts
        )

    if "error" in ai_response:
        return JSONResponse(
            status_code=500,
            content={"error": "AI returned invalid response", "details": ai_response}
        )

    # STEP 4 — Build final response
    final_response = {
        "status": "success",
        "message": "Task Report Generated Successfully",
        "data": {
            "task_id": task_id,
            "task_generated_date": task_prd.get("task_date"),
            "priority": task_prd.get("priority"),
            "key_highlights": ai_response.get("key_highlights"),
            "upcoming_tasks": ai_response.get("upcoming_tasks"),
            "suggestions": ai_response.get("suggestions"),
            "eta": task_prd.get("eta")
        }
    }


    return final_response