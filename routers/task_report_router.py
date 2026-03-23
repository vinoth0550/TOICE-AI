

# phase 2 

# task_report_router.py


from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import asyncio

from database import  task_chat_collection, task_collection, task_report_collection, activity_collection  ## activity_collection for int act
from gemini_service import generate_task_report
from concurrency_limit import semaphore, logger
import json


######
from utils import (
     validate_transcript
)
from bson import ObjectId

######


# mp3 #

import os
from dotenv import load_dotenv
import requests
from gemini_service import transcribe_audio

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

# mp3 #



# mp3 #


def download_audio(url: str):

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        return response.content

    except Exception as e:

        logger.error(f"Audio download failed: {url} | {str(e)}")
        return None


# mp3 #



#### To reduce the latency ####


async def process_audio_attachment(sender, full_url):

    logger.info(f"Downloading audio: {full_url}")

    audio_bytes = await asyncio.to_thread(download_audio, full_url)

    if not audio_bytes:
        return None

    logger.info("Transcribing audio...")

    async with semaphore:
        transcript = await asyncio.to_thread(transcribe_audio, audio_bytes)

    logger.info(f"Chat audio transcript: {transcript}")

    if not validate_transcript(transcript):
        logger.warning("Chat audio contains no valid speech")
        return None

    return f"{sender} (audio): {transcript}"


#### To reduce the latency ####




# HTML

def generate_html_report(data: dict) -> str:

    priority_color = {
        "High": "#c0392b",
        "HIGH": "#c0392b",
        "Medium": "#f39c12",
        "Low": "#27ae60"
    }.get(data.get("priority"), "#1f4e79")

    key_highlights_html = "".join(
        [f"<li>{item}</li>" for item in data.get("key_highlights", [])]
    )

    upcoming_tasks_html = "".join(
        [f"<li>{item}</li>" for item in data.get("upcoming_tasks", [])]
    )

    suggestions_html = "".join(
        [f"<li>{item}</li>" for item in data.get("suggestions", [])]
    )

    html = f"""
<div style="font-family:Arial, Helvetica, sans-serif; background:#0C6653; padding:20px; border-radius:10px; color:#333; max-width:800px; margin:auto;">

<div style="margin-bottom:10px;">
<h2 style="color:#ffffff; margin-bottom:3px;">📋 Task Report</h2>

<p style="font-size:13px; color:#d1f2eb; margin:0;">

<strong>🕒 Generated on:</strong> {data.get("task_generated_date")}
</p>
</div>

<div style="background:#ffffff; padding:15px; border-radius:8px; margin-top:15px; box-shadow:0 2px 5px rgba(0,0,0,0.08);">

<p><strong>🆔 Task ID:</strong> {data.get("task_id")}</p>
<p><strong>👥 Group ID:</strong> {data.get("group_id")}</p>
<p><strong>👤 Assignee:</strong> {data.get("assignee")}</p>

<p>
<strong>🔥 Priority:</strong>
<span style="color:{priority_color}; font-weight:bold;">
{data.get("priority")}
</span>
</p>

<p><strong>📅 ETA:</strong> {data.get("eta")}</p>

</div>


<div style="margin-top:15px; padding:15px; background:#ffffff; border-radius:8px;">
<h3 style="color:#1f4e79;">📌 Key Highlights</h3>

<ul style="
padding-left:18px;
margin:0;
line-height:1.6;
word-break:break-word;
overflow-wrap:anywhere;
white-space:normal;
">
{key_highlights_html}
</ul>

<div style="margin-top:15px; padding:15px; background:#ffffff; border-radius:8px;">
<h3 style="color:#1f4e79;">🔜 Upcoming Tasks</h3>

<ul style="
padding-left:18px;
margin:0;
line-height:1.6;
word-break:break-word;
overflow-wrap:anywhere;
white-space:normal;
">
{upcoming_tasks_html}
</ul>


<div style="margin-top:15px; padding:15px; background:#ffffff; border-radius:8px;">
<h3 style="color:#1f4e79;">📝 Task Summary</h3>

<p style="
line-height:1.7;
margin:0;
word-break:break-word;
overflow-wrap:anywhere;
white-space:normal;
">
{data.get("task_summary")}
</p>

</div>

<div style="margin-top:15px; padding:15px; background:#ffffff; border-radius:8px;">
<h3 style="color:#1f4e79;">🚀 Suggestions</h3>


<ul style="
padding-left:18px;
margin:0;
line-height:1.6;
word-break:break-word;
overflow-wrap:anywhere;
white-space:normal;
">
{suggestions_html}
</ul>


</div>
"""

    return html.replace("\n", "")

# HTML
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



    # Fetch task PRD

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

 



    task_prd = task_doc["data"]
    ##### int-act 2.1
    assignee = task_prd.get("to", "")
    ##### int-act 2.1



    # Convert ObjectId to string
    task_prd = json.loads(json.dumps(task_prd, default=str))


    ####

    # Fetch chats sorted ASC

    ###
    logger.info("Fetching task chats from database...")
    ###


    ####

    fetch_chats = task_chat_collection.find(
        {"task_id": task_object_id}
    ).sort("createdAt", 1)

    chats = list(fetch_chats)




    if not chats:
        logger.warning(f"No chats found, proceeding with activity logs only | task_id={task_id}")
        chats = []


#### to process the task report eventhough that task_id has no chat_messgaes by using chat activities it need to generate


    ####

    #### updated chat file download to avoid the latency issues

    chat_texts = []
    tasks = []

    for chat in chats:

        sender = str(chat.get("MsgFrom_id"))

        # TEXT MESSAGE
        if chat.get("message"):
            chat_texts.append(f"{sender}: {chat.get('message')}")

        attachments = chat.get("attachments", [])


        #####  to process the only audio file in this phase 2

        for file in attachments:

            file_url = file.get("fileUrl")

            if not file_url:
                continue

            #  ONLY process audio files
            if not file_url.lower().endswith((".mp3", ".wav", ".ogg")):
                logger.info(f"Skipping non-audio file: {file_url}")
                continue

            full_url = f"{BASE_URL}/{file_url}"

            tasks.append(
                process_audio_attachment(sender, full_url)
            )

        #####  to process the only audio file in this phase 2

    # Run audio processing in parallel
    results = await asyncio.gather(*tasks)

    for r in results:
        if r:
            chat_texts.append(r)

    #### updated chat file download to avoid the latency issues

    # mp3 #





    ##### int-act 3.1

   
    # FETCH ACTIVITIES


    activities = list(activity_collection.find({
        "entityId": task_object_id,
        "entityType": "TASK"
    }).sort("meta.createdAt", 1))

    activity_logs = []

    for act in activities:
        user = act.get("performedByInfo", {}).get("name", "Unknown")
        message = act.get("message", "")

        activity_logs.append(f"{user}: {message}")

    logger.info(f"Activities fetched: {activity_logs}")

    ##### int-act 3.1







    ##### int-act 4

    # DELAY DETECTION


    

    delay_info = "on_time"

    eta = task_prd.get("eta")

    try:
        eta_date = datetime.strptime(eta, "%d/%m/%Y")
        if datetime.utcnow() > eta_date:
            delay_info = "delayed"
    except:
        pass

    logger.info(f"Task delay status: {delay_info}")

    ##### int-act 4




    #  Call AI

    async with semaphore:
        ai_response = await safe_run_with_timeout(
            # generate_task_report,
            # task_prd,
            # chat_texts

            ##### int-act 5.1
            generate_task_report,
            task_prd,
            chat_texts,activity_logs,delay_info
        )
            ##### int-act 5.1

    if "error" in ai_response:
        return JSONResponse(
            status_code=500,
            content={"error": "AI returned invalid response", "details": ai_response}
        )

    # Build final response


    ###
    logger.info("Sending data to AI for report generation...")
    ###


    ##### to avoid the emty array




    key_highlights = ai_response.get("key_highlights")
    upcoming_tasks = ai_response.get("upcoming_tasks")
    suggestions = ai_response.get("suggestions")
    task_summary = ai_response.get("task_summary")

    if not key_highlights:
        key_highlights = ["Task progress could not be clearly determined from the chat history."]

    if not upcoming_tasks:
        upcoming_tasks = ["No pending tasks identified from current discussion."]

    if not suggestions:
        suggestions = [
            "Improve communication clarity within the team.",
            "Ensure tasks are clearly documented and tracked."
        ]

    if not task_summary or len(task_summary.strip()) < 10:
        task_summary = "The available chat discussion was analyzed but did not provide sufficient structured updates."


    ###
    final_response = {
        "status": "true",
        "message": "Task Report Generated Successfully",
        "data": {
            "task_id": task_id,
            "group_id": task_prd.get("group_id"),

            ##### int-act 2.2
            "assignee": assignee,
            ##### int-act 2.2

            "task_generated_date": task_prd.get("task_date"),
            "priority": task_prd.get("priority"),
            "key_highlights": key_highlights,
            "upcoming_tasks": upcoming_tasks,
            "task_summary": task_summary,
            "suggestions": suggestions,
                        
            "eta": task_prd.get("eta")
        }
    }



    ##### to avoid the emty array

    
    ###
    logger.info("AI report generated successfully.")
    ###



    # return final_response
    html_report = generate_html_report(final_response["data"])

    final_response["html-report"] = {
        "html": html_report
    }

    return final_response



# { task_id: ObjectId("69b186ab467b4a60236da6c4") } this has no chat messages


# 69bb8c12918add7ad9fd05eb


# 69b2531c38b684580374c4d9                            = task id to fetch task report on postman server this id has all datas like task_prd, task_chat_messages,activities in db.

# { task_id: ObjectId("69b2531c38b684580374c4d9") }   = query to fetch this task related data's from the task_prd and task_chat_messages 

# {entityId : ObjectId('69b2531c38b684580374c4d9')}   = to fetch this task related activities from the db


# updated task report



# {
#     "status": "true",
#     "message": "Task Report Generated Successfully",
#     "data": {
#         "task_id": "69b2531c38b684580374c4d9",
#         "group_id": "69b24d8538b684580374bc4c",
#         "assignee": "Abinesh Durai Tsit, me",
#         "task_generated_date": "12/03/2026",
#         "priority": "High",
#         "key_highlights": [
#             "Task was created by Avinash",
#             "Task viewed by abinesh durai",
#             "Task viewed by Vignesh developer",
#             "Task reassigned by Vignesh developer (Reason: Member removed from group)",
#             "Task audio content listened to by Vignesh developer",
#             "All task audio content listened to by Vignesh developer"
#         ],
#         "upcoming_tasks": [
#             "Finalize Q3 budget review with the finance department.",
#             "Prepare the agenda and materials for the upcoming Project Alpha kickoff meeting.",
#             "Follow up on outstanding vendor contracts for the Phase 2 procurement.",
#             "Draft the weekly progress report for the executive steering committee."
#         ],
#         "task_summary": "The task is currently on time. The past week saw significant progress on key deliverables, with Phase 1 milestones successfully met and initial stakeholder engagement completed. We are currently transitioning into the planning stages for Phase 2, focusing on resource allocation and vendor finalization to maintain momentum and adhere to the project timeline.",
#         "suggestions": [
#             "Implement a more agile feedback loop with key stakeholders to address potential blockers proactively.",
#             "Standardize documentation templates across all project phases to improve consistency and reduce onboarding time for new team members.",
#             "Conduct a brief post-mortem on Phase 1 to capture lessons learned and apply them to subsequent phases."
#         ],
#         "eta": "2026-03-12"
#     }
# }



# 69ba910693f93feb378ebc16