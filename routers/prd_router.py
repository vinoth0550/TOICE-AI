

# # prd_router.py


# from fastapi import APIRouter, UploadFile, File, Form
# from fastapi.responses import JSONResponse
# import os
# import shutil
# from datetime import datetime,timedelta
# from gemini_service import generate_prd, transcribe_audio
# from database import save_prd,prd_collection

# # from docx import Document
# # from PyPDF2 import PdfReader
# # from pptx import Presentation
# from utils import extract_text_from_docx, extract_text_from_pdf

# # move your full generate_prd endpoint here

# router = APIRouter()

# router = APIRouter()

# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)






# @router.post("/generate-prd")
# async def generate_prd_endpoint(
#     project_id: str = Form(...),
#     sender_id: str = Form(...),
#     piriority: str = Form(...),
#     text: str = Form(None),
#     file: UploadFile = File(None)
# ):

#     raw_input_text = ""
#     transcript = None
#     input_type = None

#     # 1️⃣ If Text Provided
#     if text:
#         raw_input_text = text
#         input_type = "text"

#     # 2️⃣ If File Provided
#     if file:
#         file_path = os.path.join(UPLOAD_DIR, file.filename)

#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         if file.filename.endswith(".docx"):
#             raw_input_text = extract_text_from_docx(file_path)
#             input_type = "docx"

#         elif file.filename.endswith(".pdf"):
#             raw_input_text = extract_text_from_pdf(file_path)
#             input_type = "pdf"


#         elif file.filename.endswith(".wav") or file.filename.endswith(".mp3"):
#             audio_bytes = open(file_path, "rb").read()
#             transcript = transcribe_audio(audio_bytes)
#             raw_input_text = transcript
#             input_type = "audio"

#         else:
#             return JSONResponse(status_code=400, content={"error": "Unsupported file type"})

#     if not raw_input_text:
#         return JSONResponse(status_code=400, content={"error": "No input provided"})

#     # 3️⃣ Generate PRD JSON
#     prd_json = generate_prd(raw_input_text)



#     ###

#     report_date = datetime.utcnow().strftime("%d/%m/%Y")

#     final_response = {
#         "project_id": project_id,
#         "sender_id": sender_id,
#         "report_date": report_date,
#         "priority": piriority,
#         "key_insights": prd_json.get("key_insights"),
#         "team_tasks": prd_json.get("team_tasks"),
#         "project_overview": prd_json.get("project_overview"),
#         "suggestions": prd_json.get("suggestions")
#     }

#     ###




#    ###



#     # 1️⃣ Set correct PRD creation date
#     current_date = datetime.utcnow().strftime("%d/%m/%Y")
#     prd_json["date"] = current_date

#     # 2️⃣ Fix ETA logic
#     eta_value = prd_json.get("eta")

#     if not eta_value or "90" in str(eta_value).lower():
#         eta_date = datetime.utcnow() + timedelta(days=90)
#         prd_json["eta"] = eta_date.strftime("%d/%m/%Y")

#    ###





#     db_data = {
#         "project_id": project_id,
#         "sender_id": sender_id,
#         "priority": piriority,
#         "report_date": report_date,
#         "key_insights": prd_json.get("key_insights"),
#         "team_tasks": prd_json.get("team_tasks"),
#         "project_overview": prd_json.get("project_overview"),
#         "suggestions": prd_json.get("suggestions"),
#         "raw_input": raw_input_text,
#         "transcript": transcript,
#         "input_type": input_type,
#         "created_at": datetime.utcnow()
#     }


#     inserted_id = save_prd(db_data)


#     return {
#     "message": "Project Report Generated Successfully",
#     "mongo_id": inserted_id,
#     "data": final_response
#     }




# @router.get("/project-reports/{project_id}")
# def get_reports(project_id: str):

#     reports_cursor = prd_collection.find(
#         {"project_id": project_id},
#         {
#             "_id": 0,
#             "project_id": 1,
#             "sender_id": 1,
#             "priority": 1,
#             "report_date": 1,
#             "key_insights": 1,
#             "team_tasks": 1,
#             "project_overview": 1,
#             "suggestions": 1
#         }
#     )

#     reports = list(reports_cursor)

#     return {
#         "project_id": project_id,
#         "total_reports": len(reports),
#         "reports": reports
#     }




# updated code 





# prd_router.py


from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime,timedelta
from gemini_service import generate_prd, transcribe_audio
from database import save_prd,prd_collection


from utils import extract_text_from_docx, extract_text_from_pdf

#
from concurrency_limit import semaphore
import asyncio
#




####

from fastapi import HTTPException
from google.genai.errors import APIError, ServerError


async def safe_run_with_timeout(func, arg, timeout: int = 10):
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


# move your full generate_prd endpoint here

router = APIRouter()

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)






@router.post("/generate-prd")
async def generate_prd_endpoint(
    project_id: str = Form(...),
    sender_id: str = Form(...),
    piriority: str = Form(...),
    text: str = Form(None),
    file: UploadFile = File(None)
):



    #  Validate input combination
    if text and file:
        return JSONResponse(
            status_code=400,
            content={"error": "Please provide either text or file, not both."}
        )

    if not text and not file:
        return JSONResponse(
            status_code=400,
            content={"error": "Either text or file is required."}
        )



    raw_input_text = ""
    transcript = None
    input_type = None

    # 1️⃣ If Text Provided
    if text:
        raw_input_text = text
        input_type = "text"

    # 2️⃣ If File Provided
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
        prd_json = await safe_run_with_timeout(
            generate_prd,
            raw_input_text,
            timeout=120   # can adjust minutes
        )

        



    if "error" in prd_json:
        return JSONResponse(
            status_code=500,
            content={"error": "AI returned invalid response", "details": prd_json}
        )


    ###

    report_date = datetime.utcnow().strftime("%d/%m/%Y")




    #  Remove empty team arrays
    team_tasks = prd_json.get("team_tasks", {})

    cleaned_team_tasks = {
        team: tasks
        for team, tasks in team_tasks.items()
        if tasks and len(tasks) > 0
    }



    final_response = {
        "project_id": project_id,
        "sender_id": sender_id,
        "report_date": report_date,
        "priority": piriority,
        "key_insights": prd_json.get("key_insights"),
     
        "team_tasks": cleaned_team_tasks,
   

        "project_overview": prd_json.get("project_overview"),
        "suggestions": prd_json.get("suggestions")
    }


    #  Set correct PRD creation date
    current_date = datetime.utcnow().strftime("%d/%m/%Y")
    prd_json["date"] = current_date




    # Fix ETA logic
    eta_value = prd_json.get("eta")

    if not eta_value or "90" in str(eta_value).lower():
        eta_date = datetime.utcnow() + timedelta(days=90)
        prd_json["eta"] = eta_date.strftime("%d/%m/%Y")

    db_data = {
        "project_id": project_id,
        "sender_id": sender_id,
        "priority": piriority,
        "report_date": report_date,
        "key_insights": prd_json.get("key_insights"),
        "team_tasks": prd_json.get("team_tasks"),
        "project_overview": prd_json.get("project_overview"),
        "suggestions": prd_json.get("suggestions"),
        "raw_input": raw_input_text,
        "transcript": transcript,
        "input_type": input_type,
        "created_at": datetime.utcnow()
    }


    inserted_id = save_prd(db_data)


    return {
    "message": "Project Report Generated Successfully",
    
    "data": final_response
    }




@router.get("/project-reports/{project_id}")
def get_reports(project_id: str):

    reports_cursor = prd_collection.find(
        {"project_id": project_id},
        {
            "_id": 0,
            "project_id": 1,
            "sender_id": 1,
            "priority": 1,
            "report_date": 1,
            "key_insights": 1,
            "team_tasks": 1,
            "project_overview": 1,
            "suggestions": 1
        }
    )

    reports = list(reports_cursor)

    return {
        "project_id": project_id,
        "total_reports": len(reports),
        "reports": reports
    }