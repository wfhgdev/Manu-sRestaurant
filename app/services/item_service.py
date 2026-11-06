"""
Servicios: lógica de negocio reutilizable que no pertenece a una sola ruta.

Diferencia con controllers/:
- controllers/ -> operaciones directas sobre una tabla (crear, leer, actualizar, borrar).
- services/    -> reglas que combinan varias cosas. Ejemplo: "comprobar que hay
                  mesa libre antes de confirmar una reserva".

Archivo de ejemplo de la estructura base. Cuando haya un servicio real,
se crea con su propio nombre (por ejemplo booking_service.py).
"""
