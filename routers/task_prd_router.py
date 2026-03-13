


# phase 2

# task_prd_router.py

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import shutil

from gemini_service import generate_task_prd, transcribe_audio
# from database import save_task
from utils import extract_text_from_docx, extract_text_from_pdf


from concurrency_limit import semaphore,logger
import asyncio


from fastapi import HTTPException
from google.genai.errors import APIError, ServerError




## bfix

from utils import (
    check_audio_duration,
    detect_silence,
    validate_transcript
)

## bfix









async def safe_run_with_timeout(func, arg, timeout: int = 120):
    try:
        
        logger.info("Starting AI execution with timeout control...")

        return await asyncio.wait_for(
            asyncio.to_thread(func, arg),
            timeout=timeout
        )

    except ServerError as e:
        
        logger.error(f"503 ServerError: {e.message}")

        raise HTTPException(
            status_code=503,
            detail=e.message
        )

    except APIError as e:
        
        logger.error(f"G APIError: {e.message}")

        raise HTTPException(
            status_code=500,
            detail=e.message
        )

    except asyncio.TimeoutError:

        logger.error("AI task timed out.")

        raise HTTPException(
            status_code=408,
            detail="Task timed out while generating PRD."
        )

    except asyncio.CancelledError:

        logger.error("AI task cancelled unexpectedly.")

        raise HTTPException(
            status_code=500,
            detail="Task was cancelled unexpectedly."
        )

    except Exception as e:

        logger.error(f"Unexpected error during AI execution: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)



@router.post("/generate-task")

async def generate_task(
    ###
    group_id:   str = Form(...),
    ###
    task_id:    str = Form(...),
    sender_id:  str = Form(...),
    to:         str = Form(...),
    priority:   str = Form(...),
    eta:        str = Form(...),
   
    type:       str = Form(...),
    file:       UploadFile = File(...)
):
        
    logger.info(f"New request received")
    
    raw_input_text = ""
    transcript = None
    input_type = None

    
    # Check if file exists
    if not file:
        logger.warning("No file provided.")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Audio file is required"
            }
        )

    # Check file extension
    if not file.filename.lower().endswith((".wav", ".mp3", ".ogg")):
        logger.warning("Unsupported file type received.")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Only .wav, .ogg and .mp3 audio files are supported"
            }
        )

    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logger.info(f"Audio file saved | filename={file.filename}")







    ## bfix


   
    # AUDIO DURATION CHECK
 

    valid_duration, duration = check_audio_duration(file_path)

    logger.info(f"Audio duration: {duration} seconds")

    if not valid_duration:

        logger.warning("Audio shorter than minimum allowed duration")

        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Audio must be at least 2 seconds long."
            }
        )


    ## bfix







    ## bfix




    logger.info("Processing AUDIO file...")


    audio_bytes = await asyncio.to_thread(lambda: open(file_path, "rb").read())

    logger.info("Starting audio transcription...")

    transcript = transcribe_audio(audio_bytes)

    ## bfix






    ## bfix


    logger.info(f"Transcript length: {len(transcript)} characters")


    
    # TRANSCRIPT VALIDATION
  

    if not validate_transcript(transcript):

        logger.warning("Transcript validation failed")


        return JSONResponse(
            status_code=200,
            content={
                "status": "true",
                "data": {
                    "message": "upload a valid audible audio file."
                }
            }
        )

    raw_input_text = transcript
    input_type = "audio"



    ## bfix






    # timeout for request 


    logger.info("Waiting in processing queue...")

    async with semaphore:
         
         logger.info("Processing started inside semaphore...")

         logger.info("Calling AI to generate structured task report...")

         task_json = await safe_run_with_timeout(
            generate_task_prd,
            raw_input_text,
            timeout=120   # can adjust minutes
        )
   
    logger.info("AI response received successfully.")



    if "error" in task_json:

        logger.error("AI returned invalid JSON structure.")

        return JSONResponse(
            status_code=500,
            content={"error": "AI returned invalid response", "details": task_json}
        )


    task_date = datetime.utcnow().strftime("%d/%m/%Y")




    ########





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
        ###
        "group_id": group_id,
        ###
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

    "input_type": input_type
    }


    logger.info(f"Request completed successfully | task_id={task_id}")

    return {
 
        "status" : "true",
        "message": "Task Report Generated Successfully",
        "data": final_response
    }
