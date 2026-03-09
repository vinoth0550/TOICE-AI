

# phase 2 # 

# task_report_router.py


from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import asyncio

from database import  task_chat_collection, task_collection, task_report_collection
from gemini_service import generate_task_report
from concurrency_limit import semaphore, logger


######

from bson import ObjectId

######


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

    ###
    logger.info(f"Task report request received | task_id={task_id}")
    ###



    # STEP 1 — Fetch task PRD

    ###
    logger.info("Fetching task PRD from database...")
    ###


    ####

    try:
        task_object_id = ObjectId(task_id)
    except:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Invalid task_id format"
            }
        )

    task_doc = task_collection.find_one(
        {"data.task_id": task_object_id}
    )




    if not task_doc:
        logger.error(f"Task PRD not found | task_id={task_id}")
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": "mentioned task id dont have the prd not found"
            }
        )

    # task_prd = task_doc["data"]

    import json

    task_prd = task_doc["data"]

    # Convert ObjectId to string
    task_prd = json.loads(json.dumps(task_prd, default=str))


    ####




    # STEP 2 — Fetch chats sorted ASC

    ###
    logger.info("Fetching task chats from database...")
    ###


    ####

    fetch_chats = task_chat_collection.find(
        {"task_id": task_object_id}
    ).sort("createdAt", 1)

    chats = list(fetch_chats)




    if not chats:
        logger.error(f"No Chats found | task_id={task_id}")

        return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "mentioned task id dont have any chat"
        }
    )

    ####

    ####

    # chat_texts = [
    #     f"{chat.get('MsgFrom_id')}: {chat.get('message')}"
    #     for chat in chats
    # ]

    chat_texts = [
        f"{str(chat.get('MsgFrom_id'))}: {chat.get('message')}"
        for chat in chats
    ]

    ####

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


    ###
    logger.info("Sending data to AI for report generation...")
    ###



    ###
    final_response = {
        "status": "success",
        "message": "Task Report Generated Successfully",
        "data": {
            "task_id": task_id,
            "group_id": task_prd.get("group_id"),
            "task_generated_date": task_prd.get("task_date"),
            "priority": task_prd.get("priority"),
            "key_highlights": ai_response.get("key_highlights"),
            "upcoming_tasks": ai_response.get("upcoming_tasks"),
            "task_summary": ai_response.get("task_summary"),
            "suggestions": ai_response.get("suggestions"),
            "eta": task_prd.get("eta")
        }
    }

    ###
    
    ###
    logger.info("AI report generated successfully.")
    ###



    return final_response

