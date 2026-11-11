"""
Seeder de demostración: un restaurante completo con datos FIJOS.

Idea clave: los objetos se enlazan entre sí (restaurant=..., category=...,
allergens=[...]) en vez de escribir ids a mano. SQLAlchemy rellena solo las
claves foráneas (id_rest_..., id_cat_...) y las tablas intermedias
(rel_allergen, menu_detail, table_rel, shift_table_rel).

Se puede ejecutar varias veces: si el restaurante (por su CIF) ya existe,
no hace nada.
"""
from datetime import date, time, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    BookingModel,
    CategoryModel,
    DishModel,
    MenuModel,
    RestaurantModel,
    RestaurantTableModel,
    ShiftAssignmentModel,
    ShiftModel,
    UserModel,
)
from app.core.security import hash_password
from app.schemas.enums import BookingState, ShiftName, TableLocation, UserRole
from seeders import allergen_seeder

DEMO_CIF = "B30000001"


def seed(db: Session) -> bool:
    """Crea el restaurante de demo. Devuelve False si ya existía."""

    # 0. ¿Ya está creado? Entonces no hacemos nada (evita duplicados).
    if db.scalar(select(RestaurantModel).where(RestaurantModel.cif_rest == DEMO_CIF)):
        return False

    # 1. Alérgenos (datos comunes a todos los restaurantes)
    al = allergen_seeder.seed(db)

    # 2. El restaurante: el "padre" de casi todas las tablas
    manus = RestaurantModel(
        cif_rest=DEMO_CIF,
        name_rest="Manu's Restaurant",
        address_rest="Calle Mayor 1, 30001 Murcia",
        owner_rest="Manuel García",
        tel_rest="968000001",
        email_rest="info@manusrestaurant.es",
    )

    # 3. Usuarios del restaurante
    # Las contraseñas se guardan con hash (bcrypt), igual que al crear un usuario por la API
    manu = UserModel(name_user="Manuel García", email_user="manu@manusrestaurant.es",
                     pass_user=hash_password("admin1234"), role_user=UserRole.administrador, restaurant=manus)
    ana = UserModel(name_user="Ana López", email_user="ana@manusrestaurant.es",
                    pass_user=hash_password("camarero1234"), role_user=UserRole.camarero, restaurant=manus)
    luis = UserModel(name_user="Luis Pérez", email_user="luis@manusrestaurant.es",
                     pass_user=hash_password("camarero1234"), role_user=UserRole.camarero, restaurant=manus)

    # 4. Categorías de la carta
    entrantes = CategoryModel(name_cat_rest="Entrantes", restaurant=manus)
    principales = CategoryModel(name_cat_rest="Principales", restaurant=manus)
    postres = CategoryModel(name_cat_rest="Postres", restaurant=manus)
    bebidas = CategoryModel(name_cat_rest="Bebidas", restaurant=manus)

    # 5. Platos: cada uno con su categoría y su lista de alérgenos
    def plato(nombre, precio, categoria, alergenos=(), descripcion=None):
        return DishModel(
            name_dish=nombre,
            price_dish=Decimal(precio),
            desc_dish=descripcion,
            restaurant=manus,
            category=categoria,
            allergens=[al[a] for a in alergenos],
        )

    croquetas = plato("Croquetas de jamón", "9.50", entrantes, ["Gluten", "Lácteos", "Huevos"],
                      "6 unidades caseras")
    ensalada = plato("Ensalada mixta", "8.00", entrantes, ["Huevos", "Pescado"])
    paella = plato("Paella mixta", "16.50", principales, ["Crustáceos", "Moluscos", "Pescado"],
                   "Mínimo 2 personas, precio por persona")
    entrecot = plato("Entrecot a la brasa", "22.00", principales, [],
                     "Con patatas y pimientos")
    tarta = plato("Tarta de queso", "6.00", postres, ["Lácteos", "Huevos", "Gluten"])
    flan = plato("Flan casero", "4.50", postres, ["Huevos", "Lácteos"])
    agua = plato("Agua mineral", "2.00", bebidas)
    cana = plato("Caña de cerveza", "2.50", bebidas, ["Gluten"])

    # 6. Menú del día: la lista de platos rellena la tabla menu_detail
    MenuModel(name_menu="Menú del día", price_menu=Decimal("13.90"), restaurant=manus,
              dishes=[ensalada, paella, flan, agua])

    # 7. Mesas
    def mesa(nombre, capacidad, zona):
        return RestaurantTableModel(name_table=nombre, cap_table=capacidad,
                                    location_table=zona, restaurant=manus)

    mesa1 = mesa("Mesa 1", 2, TableLocation.interior)
    mesa2 = mesa("Mesa 2", 4, TableLocation.interior)
    mesa3 = mesa("Mesa 3", 6, TableLocation.interior)
    terraza1 = mesa("Terraza 1", 4, TableLocation.terraza)
    terraza2 = mesa("Terraza 2", 4, TableLocation.terraza)

    # 8. Turnos
    turno_manana = ShiftModel(name_shift=ShiftName.manana, open_time_shift=time(12, 0),
                              close_time_shift=time(16, 30), restaurant=manus)
    turno_tarde = ShiftModel(name_shift=ShiftName.tarde, open_time_shift=time(20, 0),
                             close_time_shift=time(23, 59), restaurant=manus)

    # 9. Asignación de turnos: qué camarero, qué día y qué mesas (tabla shift_table_rel)
    hoy = date.today()
    ShiftAssignmentModel(user=ana, shift=turno_manana, date_assign=hoy,
                         tables=[mesa1, mesa2, mesa3])
    ShiftAssignmentModel(user=luis, shift=turno_tarde, date_assign=hoy,
                         tables=[terraza1, terraza2])

    # 10. Reservas (las mesas reservadas rellenan la tabla table_rel)
    BookingModel(restaurant=manus, name_client_booking="Familia Martínez",
                 date_booking=hoy + timedelta(days=1), start_time_booking=time(14, 0),
                 qty_booking=6, state_booking=BookingState.confirmada, tables=[mesa3])
    BookingModel(restaurant=manus, name_client_booking="Laura Sánchez",
                 date_booking=hoy + timedelta(days=1), start_time_booking=time(21, 30),
                 qty_booking=2, state_booking=BookingState.pendiente, tables=[terraza1])
    BookingModel(restaurant=manus, name_client_booking="Pedro Ruiz",
                 date_booking=hoy + timedelta(days=2), start_time_booking=time(13, 30),
                 qty_booking=4, state_booking=BookingState.cancelada, tables=[mesa2])

    # 11. Guardar. Añadiendo el restaurante se guarda todo lo enlazado a él.
    #     Todo va en una sola transacción: si algo falla, no se guarda nada.
    db.add(manus)
    db.commit()
    return True
