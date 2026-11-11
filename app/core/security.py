"""Seguridad: contraseñas con hash."""
import bcrypt


def hash_password(password: str) -> str:
    """Convierte la contraseña en un hash para guardarla en la base de datos."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Comprueba si la contraseña escrita coincide con el hash guardado."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
