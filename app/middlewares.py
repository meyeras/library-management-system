from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as http_exception:
        return JSONResponse(status_code=http_exception.status_code, content={"detail": http_exception.detail})
    except IntegrityError as integrity_error:
        print("IntegrityError:", integrity_error)
        return JSONResponse(status_code=400, content={"detail": "IntegrityError occurred"})
    except SQLAlchemyError as db_exception:
        print("SQLAlchemy exception:", db_exception)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    except Exception as exception:
        print("Exception:", exception)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

