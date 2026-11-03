from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.restaurant_model import RestaurantModel
from app.schemas.restaurant_schema import RestaurantCreate, RestaurantUpdate


def get_restaurants(db: Session, skip: int = 0, limit: int = 100) -> list[RestaurantModel]:
    return list(db.execute(select(RestaurantModel).offset(skip).limit(limit)).scalars().all())


def get_restaurant_by_id(db: Session, id_rest: int) -> RestaurantModel | None:
    return db.execute(select(RestaurantModel).where(RestaurantModel.id_rest == id_rest)).scalar_one_or_none()


def get_restaurant_by_cif(db: Session, cif_rest: str) -> RestaurantModel | None:
    return db.execute(select(RestaurantModel).where(RestaurantModel.cif_rest == cif_rest)).scalar_one_or_none()


def create_restaurant(db: Session, restaurant: RestaurantCreate) -> RestaurantModel:
    if get_restaurant_by_cif(db, restaurant.cif_rest):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El CIF '{restaurant.cif_rest}' ya está registrado"
        )

    db_restaurant = RestaurantModel(
        cif_rest=restaurant.cif_rest,
        name_rest=restaurant.name_rest,
        address_rest=restaurant.address_rest,
        owner_rest=restaurant.owner_rest,
        tel_rest=restaurant.tel_rest,
        email_rest=restaurant.email_rest,
    )
    try:
        db.add(db_restaurant)
        db.commit()
        db.refresh(db_restaurant)
        return db_restaurant
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def update_restaurant(db: Session, id_rest: int, restaurant_update: RestaurantUpdate) -> RestaurantModel:
    db_restaurant = get_restaurant_by_id(db, id_rest)
    if not db_restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante con id_rest {id_rest} no encontrado"
        )

    update_data = restaurant_update.model_dump(exclude_unset=True)

    if "cif_rest" in update_data and update_data["cif_rest"] != db_restaurant.cif_rest:
        if get_restaurant_by_cif(db, update_data["cif_rest"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El CIF '{update_data['cif_rest']}' ya está en uso"
            )

    for field, value in update_data.items():
        setattr(db_restaurant, field, value)

    try:
        db.commit()
        db.refresh(db_restaurant)
        return db_restaurant
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def delete_restaurant(db: Session, id_rest: int) -> dict[str, str]:
    db_restaurant = get_restaurant_by_id(db, id_rest)
    if not db_restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante con id_rest {id_rest} no encontrado"
        )

    try:
        db.delete(db_restaurant)
        db.commit()
        return {"message": f"Restaurante con id_rest {id_rest} eliminado exitosamente"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el restaurante porque tiene registros asociados (usuarios, platos, mesas, etc.)."
        )

