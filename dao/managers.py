# from abc import ABC, abstractmethod
from .objetos.abstracts import BaseModel
from .conn import Database
from .objetos import Paciente, Medico, Habitacion, Movimiento, Cama

class BaseManager:
    model: BaseModel
    conn: Database = Database
    keys: tuple[str, ...]
    table_name: str

    def __init__(self, model: BaseModel):
        self.model = model

    def create_object(self, data: dict) -> BaseModel:
        self.model = self.model(**data)
        return self.model

    def create(self, data: dict) -> BaseModel:
        row = self.conn.execute(f"INSERT INTO {self.table_name} ({', '.join(self.keys[1:])}) VALUES (?, ?, ?)", (data[key] for key in self.keys[1:]), single=True)
        results = dict(zip(self.keys, row))
        return self.create_object(results)

    def get(self, id: int) -> BaseModel:
        row = self.conn.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (id,), single=True)
        results = dict(zip(self.keys, row))
        return self.create_object(results)

    def list(self) -> list[BaseModel]:
        rows = self.conn.execute(f"SELECT * FROM {self.table_name}")
        return [self.create_object(dict(zip(self.keys, row))) for row in rows]

    def filter(self, **kwargs) -> list[BaseModel]:
        params = []
        conditions = []
        for key, value in kwargs.items():
            conditions.append(f"{key} = ?")
            params.append(value)
        query = f"SELECT * FROM {self.table_name} WHERE {' AND '.join(conditions)}"
        rows = self.conn.execute(query, params)
        return [self.create_object(dict(zip(self.keys, row))) for row in rows]

    def update(self, id: int, data: dict) -> BaseModel:
        set_clause = ", ".join(f"{key} = ?" for key in data.keys())
        params = list(data.values())
        params.append(id)
        self.conn.execute(f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?", params)
        return self.get(id)

    def delete(self, id: int) -> None:
        self.conn.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (id,))

class PacienteManager(BaseManager):
    model = Paciente
    keys = ("id", "nombre", "edad", "genero")
    table_name = "pacientes"

    def create(self, data: dict) -> Paciente:
        return super().create(data)

    def get(self, id: int) -> Paciente:
        row = self.conn.execute("SELECT * FROM pacientes WHERE id = ?", (id,), single=True)
        results = dict(zip(self.keys, row))
        return self.create_object(results)