from dataclasses import dataclass
from datetime import datetime

@dataclass
class Movimiento:
    id: int
    id_cama: int
    id_paciente: int
    id_medico: int
    fecha_ingreso: datetime
    fecha_egreso: datetime
    
    def to_dict(self):
        return {
            "id": self.id,
            "id_cama": self.id_cama,
            "id_paciente": self.id_paciente,
            "id_medico": self.id_medico,
            "fecha_ingreso": self.fecha_ingreso,
            "fecha_egreso": self.fecha_egreso
        }

    def __str__(self):
        return f"Movimiento: {self.id}"