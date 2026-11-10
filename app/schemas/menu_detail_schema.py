from pydantic import BaseModel, ConfigDict


class MenuDetailBase(BaseModel):
    id_menu_det: int
    id_dish_det: int


class MenuDetailCreate(MenuDetailBase):
    pass


class MenuDetailResponse(MenuDetailBase):
    model_config = ConfigDict(from_attributes=True)
    
    
