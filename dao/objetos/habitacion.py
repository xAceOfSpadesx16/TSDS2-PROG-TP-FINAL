from dataclasses import dataclass
from .abstracts import BaseModel

@dataclass
class Habitacion(BaseModel):
    id: int
    numero: int
    tipo: str
    capacidad: int

    def __init__(self, id: int, numero: int, tipo: str, capacidad: int):
        self.id = id
        self.numero = numero
        self.tipo = tipo
        self.capacidad = capacidad

    def to_dict(self):
        return {
            "id": self.id,
            "numero": self.numero,
            "tipo": self.tipo,
            "capacidad": self.capacidad
        }

    def __str__(self):
        return f"Habitación {self.numero} - {self.tipo} (Cap.: {self.capacidad})"