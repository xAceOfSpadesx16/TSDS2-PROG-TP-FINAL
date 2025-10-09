from dataclasses import dataclass

@dataclass
class Paciente:
    id: int
    nombre: str
    obra_social: str
    numero_afiliado: str
    domicilio: str
    telefono: str

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "obra_social": self.obra_social,
            "numero_afiliado": self.numero_afiliado,
            "domicilio": self.domicilio,
            "telefono": self.telefono
        }

    def __str__(self):
        return f"Paciente: {self.nombre} (O.S.: {self.numero_afiliado})"