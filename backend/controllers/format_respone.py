from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from enum import Enum
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from functools import wraps
import traceback

T = TypeVar('T')


class StatusCode(int, Enum):
    WARNING = 202
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    FORBIDDEN = 403
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500


class ClientErrorCode:
    VALIDATION_ERROR = "VALIDATION_ERROR"


class ClientErrorDescription:
    VALIDATION_ERROR = "Invalid request"


class GenericResponse(BaseModel, Generic[T]):
    message: str
    data: Optional[T] = None


class PaginationResponse(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: int | str | None = None
    limit: int = 0


class PaginationAnyResponse(BaseModel, Generic[T]):
    items: T
    next_cursor: int | str | None = None
    limit: int = 0


class PaginationGenericResponse(GenericResponse[PaginationResponse[T]], Generic[T]):
    pass


class PaginationAnyGenericResponse(GenericResponse[PaginationAnyResponse[T]], Generic[T]):
    pass


class CoreResponseModels:

    # ----- Success -----
    @staticmethod
    def response_upload(item: T) -> JSONResponse:
        return JSONResponse(
            status_code=StatusCode.CREATED,
            content=jsonable_encoder(GenericResponse[T](message="Upload successful", data=item))
        )

    @staticmethod
    def response_one(message: Optional[str] = "Get successful", item: T = None) -> JSONResponse:
        return JSONResponse(
            status_code=StatusCode.SUCCESS,
            content=jsonable_encoder(GenericResponse[T](message=message, data=item))
        )

    @staticmethod
    def response_list(items: list[T], message: Optional[str] = "Get successful") -> JSONResponse:
        return JSONResponse(
            status_code=StatusCode.SUCCESS,
            content=jsonable_encoder(GenericResponse[list[T]](message=message, data=items))
        )

    @staticmethod
    def response_pagination(items: list[T], next_cursor: int | str | None, limit: int, message: Optional[str] = "Get successful") -> JSONResponse:
        pagination_data = PaginationResponse[T](items=items, next_cursor=next_cursor, limit=limit)
        return JSONResponse(
            status_code=StatusCode.SUCCESS,
            content=jsonable_encoder(PaginationGenericResponse[T](message=message, data=pagination_data))
        )

    @staticmethod
    def response_pagination_any(items: T, next_cursor: int | str | None, limit: int, message: Optional[str] = "Get successful") -> JSONResponse:
        pagination_data = PaginationAnyResponse[T](items=items, next_cursor=next_cursor, limit=limit)
        return JSONResponse(
            status_code=StatusCode.SUCCESS,
            content=jsonable_encoder(PaginationAnyGenericResponse[T](message=message, data=pagination_data))
        )

    @staticmethod
    def response_error(message: str, status: StatusCode = StatusCode.BAD_REQUEST) -> JSONResponse:
        return JSONResponse(
            status_code=status,
            content=jsonable_encoder(GenericResponse[None](message=message, data=None))
        )
 

def raise_validation_error(error_code: str) -> None:
    description = getattr(ClientErrorDescription, error_code, None)
    if description is None:
        description = "An unexpected validation error occurred."

    raise HTTPException(
        status_code=StatusCode.UNPROCESSABLE_ENTITY,
        detail={
            "code": error_code,
            "description": description,
            "fields": []
        }
    )