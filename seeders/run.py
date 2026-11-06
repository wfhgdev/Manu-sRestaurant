"""
Lanzador de seeders. Ejecutar SIEMPRE desde la raíz del proyecto.

    python -m seeders.run --demo         -> alérgenos + restaurante de demo (datos fijos)
    python -m seeders.run --count 100    -> 100 registros falsos en la tabla "test" (Faker)
"""
import argparse

from app.db.database import SessionLocal  # carga la BD con todos los modelos registrados
from seeders import demo_seeder, test_seeder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true",
                        help="Inserta los alérgenos y el restaurante de demostración")
    parser.add_argument("--count", type=int, default=50,
                        help="Número de registros falsos para la tabla test")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.demo:
            if demo_seeder.seed(db):
                print("Restaurante de demo creado (con carta, mesas, usuarios, turnos y reservas)")
            else:
                print("El restaurante de demo ya existía: no se ha insertado nada")
        else:
            test_seeder.seed(db, args.count)
            print(f"Seeded {args.count} records")
    finally:
        db.close()


if __name__ == "__main__":
    main()
