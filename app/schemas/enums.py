import enum


class UserRole(str, enum.Enum):
    administrador = "administrador"
    camarero = "camarero"
    superadministrador = "superadministrador"


class BookingState(str, enum.Enum):
    pendiente = "pendiente"
    confirmada = "confirmada"
    cancelada = "cancelada"


class TableLocation(str, enum.Enum):
    terraza = "terraza"
    interior = "interior"


class ShiftName(str, enum.Enum):
    manana = "mañana"
    tarde = "tarde"

