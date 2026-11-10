from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.test_model import TestModel
from app.schemas.test_schema import TestCreate

def create_test(db: Session, test: TestCreate):
    if db.execute(select(TestModel).where(TestModel.test_name == test.test_name)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un test llamado '{test.test_name}'"
        )
    db_test = TestModel(test_name=test.test_name, test_type=test.test_type)
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test