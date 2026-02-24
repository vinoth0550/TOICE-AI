
# task_router.py

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import shutil

from gemini_service import generate_task_prd, transcribe_audio
from database import save_task
from utils import extract_text_from_docx, extract_text_from_pdf

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/generate-task")
async def generate_task(
    task_id: str = Form(...),
    sender_id: str = Form(...),
    to: str = Form(...),
    piriority: str = Form(...),
    eta: str = Form(None),
    text: str = Form(None),
    file: UploadFile = File(None)
):
    
    raw_input_text = ""
    transcript = None
    input_type = None

    if text:
        raw_input_text = text
        input_type = "text"

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

    task_json = generate_task_prd(raw_input_text)


    task_date = datetime.utcnow().strftime("%d/%m/%Y")

    final_response = {
        "task_id": task_id,
        "sender_id": sender_id,
        "to": to,
        "priority": piriority,
        "task_date": task_date,
        "to_do": task_json.get("to_do"),
        "task_summary": task_json.get("task_summary"),
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
        "message": "Task Report Generated Successfully",
        "mongo_id": inserted_id,
        "data": final_response
    }