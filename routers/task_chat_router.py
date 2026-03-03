
# task_chat_router.py



from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import shutil

from gemini_service import transcribe_audio
from database import task_chat_collection
from utils import extract_text_from_docx, extract_text_from_pdf

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/task-chat")
async def save_task_chat(

    task_id: str = Form(...),
    sender_id: str = Form(...),
    text: str = Form(None),
    file: UploadFile = File(None)
):

    if text and file:
        return JSONResponse(status_code=400, content={"error": "Provide either text or file"})

    if not text and not file:
        return JSONResponse(status_code=400, content={"error": "Text or file required"})

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

        if file.filename.endswith(".wav") or file.filename.endswith(".mp3"):
            audio_bytes = open(file_path, "rb").read()
            transcript = transcribe_audio(audio_bytes)
            raw_input_text = transcript
            input_type = "audio"
        else:
            return JSONResponse(status_code=400, content={"error": "Only audio allowed"})

    task_chat_collection.insert_one({

        "task_id":task_id,  
        "sender_id": sender_id,
        "message": raw_input_text,
        "input_type": input_type,
        "created_at": datetime.utcnow()
    })

    return {"message": "Chat saved successfully"}