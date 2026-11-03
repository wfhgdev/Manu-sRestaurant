from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database_connection import get_db
from app.schemas.restaurant_schema import RestaurantCreate, RestaurantUpdate, RestaurantResponse
from app.controllers import restaurant_controller

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.post("/", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
def create_new_restaurant(restaurant: RestaurantCreate, db: Session = Depends(get_db)):
    return restaurant_controller.create_restaurant(db=db, restaurant=restaurant)


@router.get("/", response_model=list[RestaurantResponse])
def get_all_restaurants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return restaurant_controller.get_restaurants(db=db, skip=skip, limit=limit)


@router.get("/{id_rest}", response_model=RestaurantResponse)
def get_restaurant(id_rest: int, db: Session = Depends(get_db)):
    restaurant = restaurant_controller.get_restaurant_by_id(db=db, id_rest=id_rest)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante con id_rest {id_rest} no encontrado"
        )
    return restaurant


@router.put("/{id_rest}", response_model=RestaurantResponse)
def update_restaurant_by_id(id_rest: int, restaurant_update: RestaurantUpdate, db: Session = Depends(get_db)):
    return restaurant_controller.update_restaurant(db=db, id_rest=id_rest, restaurant_update=restaurant_update)


@router.delete("/{id_rest}", status_code=status.HTTP_200_OK)
def delete_restaurant_by_id(id_rest: int, db: Session = Depends(get_db)):
    return restaurant_controller.delete_restaurant(db=db, id_rest=id_rest)

