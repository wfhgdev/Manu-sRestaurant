from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.booking_model import BookingModel
from app.models.restaurant_model import RestaurantModel
from app.models.table_model import TableRelModel
from app.schemas.booking_schema import BookingCreate, BookingUpdate
from app.schemas.enums import BookingState


def get_bookings(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    id_rest: int | None = None,
    date_booking: date | None = None,
    state_booking: BookingState | None = None,
) -> list[BookingModel]:
    query = select(BookingModel)
    if id_rest is not None:
        query = query.where(BookingModel.id_rest_booking == id_rest)
    if date_booking is not None:
        query = query.where(BookingModel.date_booking == date_booking)
    if state_booking is not None:
        query = query.where(BookingModel.state_booking == state_booking)
    query = query.order_by(BookingModel.date_booking, BookingModel.start_time_booking).offset(skip).limit(limit)
    return list(db.execute(query).scalars().all())


def get_booking_by_id(db: Session, id_booking: int) -> BookingModel | None:
    return db.execute(
        select(BookingModel).where(BookingModel.id_booking == id_booking)
    ).scalar_one_or_none()


def check_restaurant_exists(db: Session, id_rest: int) -> None:
    restaurant = db.execute(
        select(RestaurantModel).where(RestaurantModel.id_rest == id_rest)
    ).scalar_one_or_none()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante con id_rest {id_rest} no encontrado"
        )


def check_date_not_past(date_booking: date) -> None:
    if date_booking < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede hacer una reserva en una fecha pasada"
        )


def create_booking(db: Session, booking: BookingCreate) -> BookingModel:
    check_restaurant_exists(db, booking.id_rest_booking)
    check_date_not_past(booking.date_booking)

    db_booking = BookingModel(
        id_rest_booking=booking.id_rest_booking,
        name_client_booking=booking.name_client_booking,
        date_booking=booking.date_booking,
        start_time_booking=booking.start_time_booking,
        qty_booking=booking.qty_booking,
        state_booking=booking.state_booking,
    )
    try:
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def update_booking(db: Session, id_booking: int, booking_update: BookingUpdate) -> BookingModel:
    db_booking = get_booking_by_id(db, id_booking)
    if not db_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con id_booking {id_booking} no encontrada"
        )

    update_data = booking_update.model_dump(exclude_unset=True)

    if "date_booking" in update_data and update_data["date_booking"] != db_booking.date_booking:
        check_date_not_past(update_data["date_booking"])

    if "id_rest_booking" in update_data and update_data["id_rest_booking"] != db_booking.id_rest_booking:
        check_restaurant_exists(db, update_data["id_rest_booking"])
        # Las mesas asignadas son del restaurante anterior: no se puede cambiar de restaurante con mesas
        has_tables = db.execute(
            select(TableRelModel).where(TableRelModel.id_booking_table_rel == id_booking)
        ).first()
        if has_tables:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cambiar el restaurante de una reserva con mesas asignadas. "
                       "Quita antes sus mesas."
            )

    for field, value in update_data.items():
        setattr(db_booking, field, value)

    try:
        db.commit()
        db.refresh(db_booking)
        return db_booking
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def delete_booking(db: Session, id_booking: int) -> dict[str, str]:
    db_booking = get_booking_by_id(db, id_booking)
    if not db_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con id_booking {id_booking} no encontrada"
        )

    try:
        # Al borrar la reserva, SQLAlchemy quita también sus filas de table_rel (las mesas quedan libres)
        db.delete(db_booking)
        db.commit()
        return {"message": f"Reserva con id_booking {id_booking} eliminada exitosamente"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la reserva porque tiene registros asociados."
        )
