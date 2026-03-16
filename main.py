



# phase 2   16/03/2026 ofz

# main.py

from fastapi import FastAPI
# from routers import oprs_router, task_prd_router


from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi import Request


from concurrency_limit import logger


from routers import task_chat_router, task_report_router
from routers import  task_prd_router


app = FastAPI()

# app.include_router(oprs_router.router)
app.include_router(task_prd_router.router)


app.include_router(task_chat_router.router)
app.include_router(task_report_router.router)




@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    missing_fields = []

    for error in exc.errors():
        if error["type"] == "missing":
            missing_fields.append(error["loc"][-1])

    if missing_fields:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": f"{', '.join(missing_fields)} field(s) are required"
            }
        )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error",
            "message": "Invalid request"
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error"
        }
    )