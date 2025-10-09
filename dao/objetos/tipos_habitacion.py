from dataclasses import dataclass

@dataclass(frozen=True)
class TipoHabitacion:
    tipo: str
    capacidad: int


SALA_COMUN = TipoHabitacion(tipo="Sala Común", capacidad=4)
UCI = TipoHabitacion(tipo="UCI", capacidad=2)
PEDIATRIA = TipoHabitacion(tipo="Pediatría", capacidad=3)
OBSTETRICIA = TipoHabitacion(tipo="Ginecología y Obstetricia", capacidad=2)
NEONATOLOGIA = TipoHabitacion(tipo="Neonatología", capacidad=2)
CIRUGIA = TipoHabitacion(tipo="Cirugía", capacidad=1)
REHABILITACION = TipoHabitacion(tipo="Rehabilitación", capacidad=1)
PALIATIVOS = TipoHabitacion(tipo="Paliativos", capacidad=1)