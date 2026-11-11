"""
Manejadores de errores globales de la API.

Recogen los errores de la base de datos que no se han controlado en los
controllers y los convierten en una respuesta clara, en lugar de un
"500 Internal Server Error". Por ejemplo:

- GET /restaurants/99999999999 -> número demasiado grande para la base de datos
- un texto más largo de lo que admite su columna
- GET /bookings/?skip=-1       -> paginación negativa
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from psycopg import errors as pg_errors
from sqlalchemy.exc import DataError, IntegrityError


async def data_error_handler(request: Request, exc: DataError) -> JSONResponse:
    original = exc.orig
    if isinstance(original, pg_errors.NumericValueOutOfRange):
        detail = "Algún número enviado es demasiado grande para la base de datos"
    elif isinstance(original, pg_errors.StringDataRightTruncation):
        detail = "Algún texto enviado supera la longitud máxima permitida"
    elif isinstance(original, (pg_errors.InvalidRowCountInLimitClause, pg_errors.InvalidRowCountInResultOffsetClause)):
        detail = "Los parámetros skip y limit no pueden ser negativos"
    else:
        detail = "Algún dato enviado no es válido para la base de datos"
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": detail})


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    # Solo llega aquí si un controller no lo ha controlado antes (por ejemplo, un valor único repetido)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "La operación entra en conflicto con datos existentes (valor repetido o registro relacionado)"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DataError, data_error_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
