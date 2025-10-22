from dataclasses import dataclass
from .abstracts import BaseModel

@dataclass
class Cama(BaseModel):
    id: int
    habitacion_id: int

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "habitacion_id": self.habitacion_id
        }
    
    def __str__(self) -> str:
        return f"Cama {self.id} - Habitación: {self.habitacion_id}"