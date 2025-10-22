from dataclasses import dataclass
from .abstracts import BaseModel

@dataclass
class Habitacion(BaseModel):
    id: int
    numero: int
    tipo: str
    capacidad: int

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "numero": self.numero,
            "tipo": self.tipo,
            "capacidad": self.capacidad
        }

    def __str__(self) -> str:
        return f"Habitación {self.numero} - {self.tipo} (Cap.: {self.capacidad})"