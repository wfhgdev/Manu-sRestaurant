from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.table_model import TableRelModel, RestaurantTableModel
from app.models.booking_model import BookingModel
from app.schemas.table_rel_schema import TableRelCreate, TableRelUpdate
from app.schemas.enums import BookingState

# Tiempo que se considera ocupada una mesa desde la hora de inicio de la reserva
BOOKING_DURATION = timedelta(hours=2)


def get_table_rels(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    id_booking: int | None = None,
    id_table: int | None = None,
) -> list[TableRelModel]:
    query = select(TableRelModel)
    if id_booking is not None:
        query = query.where(TableRelModel.id_booking_table_rel == id_booking)
    if id_table is not None:
        query = query.where(TableRelModel.id_table_table_rel == id_table)
    query = query.order_by(TableRelModel.id_booking_table_rel, TableRelModel.id_table_table_rel)
    return list(db.execute(query.offset(skip).limit(limit)).scalars().all())


def get_table_rel(db: Session, id_booking: int, id_table: int) -> TableRelModel | None:
    return db.execute(
        select(TableRelModel).where(
            TableRelModel.id_booking_table_rel == id_booking,
            TableRelModel.id_table_table_rel == id_table,
        )
    ).scalar_one_or_none()


def get_booking_or_404(db: Session, id_booking: int) -> BookingModel:
    booking = db.execute(
        select(BookingModel).where(BookingModel.id_booking == id_booking)
    ).scalar_one_or_none()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con id_booking {id_booking} no encontrada"
        )
    return booking


def get_table_or_404(db: Session, id_table: int) -> RestaurantTableModel:
    table = db.execute(
        select(RestaurantTableModel).where(RestaurantTableModel.id_table == id_table)
    ).scalar_one_or_none()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mesa con id_table {id_table} no encontrada"
        )
    return table


def check_table_is_free(db: Session, booking: BookingModel, id_table: int) -> None:
    # Reservas activas (no canceladas) de esa mesa en el mismo día, sin contar esta reserva
    other_bookings = db.execute(
        select(BookingModel)
        .join(TableRelModel, TableRelModel.id_booking_table_rel == BookingModel.id_booking)
        .where(
            TableRelModel.id_table_table_rel == id_table,
            BookingModel.id_booking != booking.id_booking,
            BookingModel.date_booking == booking.date_booking,
            BookingModel.state_booking != BookingState.cancelada,
        )
    ).scalars().all()

    start = datetime.combine(booking.date_booking, booking.start_time_booking)
    for other in other_bookings:
        other_start = datetime.combine(other.date_booking, other.start_time_booking)
        # Si las dos reservas empiezan con menos de 2 horas de diferencia, se pisan
        if abs(start - other_start) < BOOKING_DURATION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La mesa {id_table} ya está ocupada a esa hora por la reserva {other.id_booking} "
                       f"({other.start_time_booking.strftime('%H:%M')})"
            )


def validate_table_rel(db: Session, id_booking: int, id_table: int) -> None:
    """Comprueba todas las reglas antes de asignar la mesa id_table a la reserva id_booking."""
    booking = get_booking_or_404(db, id_booking)
    table = get_table_or_404(db, id_table)

    if table.id_rest_table != booking.id_rest_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La mesa y la reserva son de restaurantes distintos"
        )
    if booking.state_booking == BookingState.cancelada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden asignar mesas a una reserva cancelada"
        )
    if not table.state_table:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La mesa {id_table} está desactivada"
        )
    if get_table_rel(db, id_booking, id_table):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La mesa {id_table} ya está asignada a la reserva {id_booking}"
        )

    check_table_is_free(db, booking, id_table)


def create_table_rel(db: Session, rel: TableRelCreate) -> TableRelModel:
    validate_table_rel(db, rel.id_booking_table_rel, rel.id_table_table_rel)

    db_rel = TableRelModel(
        id_booking_table_rel=rel.id_booking_table_rel,
        id_table_table_rel=rel.id_table_table_rel,
    )
    try:
        db.add(db_rel)
        db.commit()
        db.refresh(db_rel)
        return db_rel
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def update_table_rel(db: Session, id_booking: int, id_table: int, rel_update: TableRelUpdate) -> TableRelModel:
    db_rel = get_table_rel(db, id_booking, id_table)
    if not db_rel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La mesa {id_table} no está asignada a la reserva {id_booking}"
        )

    update_data = rel_update.model_dump(exclude_unset=True, exclude_none=True)
    new_id_booking = update_data.get("id_booking_table_rel", id_booking)
    new_id_table = update_data.get("id_table_table_rel", id_table)

    # Si no cambia nada, se devuelve tal cual
    if new_id_booking == id_booking and new_id_table == id_table:
        return db_rel

    validate_table_rel(db, new_id_booking, new_id_table)

    db_rel.id_booking_table_rel = new_id_booking
    db_rel.id_table_table_rel = new_id_table

    try:
        db.commit()
        db.refresh(db_rel)
        return db_rel
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def delete_table_rel(db: Session, id_booking: int, id_table: int) -> dict[str, str]:
    db_rel = get_table_rel(db, id_booking, id_table)
    if not db_rel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La mesa {id_table} no está asignada a la reserva {id_booking}"
        )

    try:
        db.delete(db_rel)
        db.commit()
        return {"message": f"Mesa {id_table} quitada de la reserva {id_booking} exitosamente"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede quitar la mesa de la reserva por restricciones de integridad."
        )
