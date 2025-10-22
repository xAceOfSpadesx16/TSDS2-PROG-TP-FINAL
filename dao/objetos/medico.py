from dataclasses import dataclass


@dataclass
class Medico:
    id: int
    nombre: str
    matricula: int
    especialidad: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "matricula": self.matricula,
            "especialidad": self.especialidad
        }
    
    def __str__(self) -> str:
        return f"Dr. {self.nombre} - {self.especialidad} (Matricula: {self.matricula})"