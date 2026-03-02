




# task_router.py

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import shutil

from gemini_service import generate_task_prd, transcribe_audio
from database import save_task
from utils import extract_text_from_docx, extract_text_from_pdf

#
from concurrency_limit import semaphore
import asyncio
#


####

from fastapi import HTTPException
from google.genai.errors import APIError, ServerError


async def safe_run_with_timeout(func, arg, timeout: int = 120):
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(func, arg),
            timeout=timeout
        )

    except ServerError as e:
        # Gemini 503 error
        raise HTTPException(
            status_code=503,
            detail=e.message
        )

    except APIError as e:
        # Gemini internal API error
        raise HTTPException(
            status_code=500,
            detail=e.message
        )

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Task timed out while generating PRD."
        )

    except asyncio.CancelledError:
        raise HTTPException(
            status_code=500,
            detail="Task was cancelled unexpectedly."
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

####



router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)



@router.post("/generate-task")
async def generate_task(
    task_id:    str = Form(...),
    sender_id:  str = Form(...),
    to:         str = Form(...),
    priority:   str = Form(...),
    eta:        str = Form(...),
   
    type:       str = Form(...),
    file:       UploadFile = File(...)
):
        


    
    raw_input_text = ""
    transcript = None
    input_type = None


    if file:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if file.filename.endswith(".docx"):
            raw_input_text = extract_text_from_docx(file_path)
            input_type = "docx"

        elif file.filename.endswith(".pdf"):
            raw_input_text = extract_text_from_pdf(file_path)
            input_type = "pdf"

        elif file.filename.endswith(".wav") or file.filename.endswith(".mp3"):
            audio_bytes = open(file_path, "rb").read()
            transcript = transcribe_audio(audio_bytes)
            raw_input_text = transcript
            input_type = "audio"

        else:
            return JSONResponse(status_code=400, content={"error": "Unsupported file type"})
           
    if not raw_input_text:
        return JSONResponse(status_code=400, content={"error": "No input provided"})

    # timeout for request 

    async with semaphore:
         task_json = await safe_run_with_timeout(
            generate_task_prd,
            raw_input_text,
            timeout=120   # can adjust minutes
        )



    if "error" in task_json:
        return JSONResponse(
            status_code=500,
            content={"error": "AI returned invalid response", "details": task_json}
        )


    task_date = datetime.utcnow().strftime("%d/%m/%Y")





    to_do_data = task_json.get("to_do", [])

    # If Gemini already returns list
    if isinstance(to_do_data, list):
        cleaned_to_do = to_do_data

    # If Gemini returns dictionary (old format)
    elif isinstance(to_do_data, dict):
        cleaned_to_do = []
        for tasks in to_do_data.values():
            if tasks:
                cleaned_to_do.extend(tasks)

    else:
        cleaned_to_do = []



    task_summary = task_json.get("task_summary", "")


    if isinstance(task_summary, str):
        task_summary = task_summary.replace("\n", " ").strip()


    final_response = {
        "task_id": task_id,
        "sender_id": sender_id,
        "to": to,
        "priority": priority,
        "task_date": task_date,
        
        "to_do": cleaned_to_do,
        "type":type,
        "task_summary" : task_summary,
        "suggestions": task_json.get("suggestions"),
        "eta": eta
    }

    db_data = {
    **final_response,
    "raw_input": raw_input_text,
    "transcript": transcript,
    "input_type": input_type
    }

    inserted_id = save_task(db_data)

    return {
 
        "status" : "success",
        "message": "Task Report Generated Successfully",
        "data": final_response
    }