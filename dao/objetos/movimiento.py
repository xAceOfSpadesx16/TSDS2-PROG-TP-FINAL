from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Movimiento:
    id: int
    cama_id: int
    paciente_id: int
    medico_id: int
    fecha_ingreso: datetime
    fecha_egreso: Optional[datetime]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "cama_id": self.cama_id,
            "paciente_id": self.paciente_id,
            "medico_id": self.medico_id,
            "fecha_ingreso": self.fecha_ingreso,
            "fecha_egreso": self.fecha_egreso
        }

    def __str__(self) -> str:
        return f"Movimiento: {self.id}"