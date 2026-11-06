from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database_connection import get_db
from app.schemas.test_schema import TestCreate
from app.controllers.test_controller import create_test


router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/", status_code=200)
def read_test():
    return {"message": "Test route"}


@router.post("/", status_code=201)
def create_new_test(test: TestCreate, db: Session = Depends(get_db)):
    return create_test(db=db, test=test)
