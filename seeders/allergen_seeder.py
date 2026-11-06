"""
Seeder de alérgenos: los 14 alérgenos de declaración obligatoria en la UE.

Son datos FIJOS (no se inventan con Faker) y comunes a todos los restaurantes.
Se puede ejecutar varias veces: solo inserta los que todavía no existen.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AllergenModel

ALLERGENS = [
    "Gluten",
    "Crustáceos",
    "Huevos",
    "Pescado",
    "Cacahuetes",
    "Soja",
    "Lácteos",
    "Frutos de cáscara",
    "Apio",
    "Mostaza",
    "Sésamo",
    "Sulfitos",
    "Altramuces",
    "Moluscos",
]


def seed(db: Session) -> dict[str, AllergenModel]:
    """Crea los alérgenos que falten y devuelve un diccionario nombre -> objeto.

    Ejemplo de uso del resultado:  allergens["Huevos"]
    """
    existing = {a.name_allergen: a for a in db.scalars(select(AllergenModel))}

    for name in ALLERGENS:
        if name not in existing:
            allergen = AllergenModel(name_allergen=name)
            db.add(allergen)
            existing[name] = allergen

    db.flush()  # les da su id sin cerrar todavía la transacción
    return existing
