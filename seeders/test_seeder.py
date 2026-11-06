from sqlalchemy.orm import Session
from seeders.factories.test_factory import make_test


def seed(db: Session, count: int = 50) -> None:
    db.add_all([make_test() for _ in range(count)])
    db.commit()
