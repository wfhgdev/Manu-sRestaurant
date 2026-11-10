from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database_connection import get_db
from app.schemas.booking_schema import BookingCreate, BookingUpdate, BookingResponse
from app.schemas.enums import BookingState
from app.controllers import booking_controller

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_new_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    return booking_controller.create_booking(db=db, booking=booking)


@router.get("/", response_model=list[BookingResponse])
def get_all_bookings(
    skip: int = 0,
    limit: int = 100,
    id_rest: int | None = None,
    date_booking: date | None = None,
    state_booking: BookingState | None = None,
    db: Session = Depends(get_db),
):
    # Filtros opcionales, por ejemplo: /bookings/?id_rest=1&date_booking=2026-11-20&state_booking=pendiente
    return booking_controller.get_bookings(
        db=db,
        skip=skip,
        limit=limit,
        id_rest=id_rest,
        date_booking=date_booking,
        state_booking=state_booking,
    )


@router.get("/{id_booking}", response_model=BookingResponse)
def get_booking(id_booking: int, db: Session = Depends(get_db)):
    booking = booking_controller.get_booking_by_id(db=db, id_booking=id_booking)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con id_booking {id_booking} no encontrada"
        )
    return booking


@router.put("/{id_booking}", response_model=BookingResponse)
def update_booking_by_id(id_booking: int, booking_update: BookingUpdate, db: Session = Depends(get_db)):
    return booking_controller.update_booking(db=db, id_booking=id_booking, booking_update=booking_update)


@router.delete("/{id_booking}", status_code=status.HTTP_200_OK)
def delete_booking_by_id(id_booking: int, db: Session = Depends(get_db)):
    return booking_controller.delete_booking(db=db, id_booking=id_booking)
