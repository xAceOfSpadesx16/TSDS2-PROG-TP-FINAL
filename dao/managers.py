# from abc import ABC, abstractmethod
from .objetos.abstracts import BaseModel
from .conn import Database
from .objetos import Paciente, Medico, Habitacion, Movimiento, Cama

class SQLBuilder:
    @staticmethod
    def build_insert_query(table_name: str, keys: tuple[str, ...]) -> str:
        placeholders = ", ".join("?" for _ in keys[1:])
        columns = ", ".join(keys[1:])
        return f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    @staticmethod
    def build_select_query(table_name: str, keys: tuple[str, ...], conditions: dict = None) -> str:
        base_query = f"SELECT * FROM {table_name}"
        if conditions:
            condition_str = " AND ".join(f"{key} = ?" for key in conditions.keys())
            return f"{base_query} WHERE {condition_str}"
        return base_query

    @staticmethod
    def build_update_query(table_name: str, keys: tuple[str, ...], id_key: str = "id") -> str:
        set_clause = ", ".join(f"{key} = ?" for key in keys if key != id_key)
        return f"UPDATE {table_name} SET {set_clause} WHERE {id_key} = ?"

    @staticmethod
    def build_delete_query(table_name: str, id_key: str = "id") -> str:
        return f"DELETE FROM {table_name} WHERE {id_key} = ?"

    @staticmethod
    def build_count_query(table_name: str) -> str:
        return f"SELECT COUNT(*) FROM {table_name}"
    


class BaseManager:
    model: BaseModel
    conn: Database = Database()
    keys: tuple[str, ...]
    table_name: str

    def __init__(self, model: BaseModel):
        self.model = model

    def create_object(self, data: dict) -> BaseModel:
        model_object = self.model(**data)
        return model_object

    def create(self, data: dict) -> BaseModel:
        # Construccion de query
        query = SQLBuilder.build_insert_query(self.table_name, self.keys)

        # Conversión de datos a tupla para guardar
        saving_data = (data[key] for key in self.keys[1:])

        # Ejecución de la query
        row = self.conn.save_execute(query, saving_data, single=True)

        # Mapeo de resultados a diccionario
        results = dict(zip(self.keys, row))
        
        return self.create_object(results)

    def get_one(self, id: int) -> BaseModel:
        row = self.conn.get_execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (id,), single=True)
        results = dict(zip(self.keys, row))
        return self.create_object(results)

    def get_list(self) -> list[BaseModel]:
        rows = self.conn.get_execute(f"SELECT * FROM {self.table_name}")
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

    def get_one(self, id: int) -> Paciente:
        return super().get_one(id)
    
    def get_list(self) -> list[Paciente]:
        return super().get_list()
    
    def filter(self, **kwargs) -> list[Paciente]:
        return super().filter(**kwargs)
    
    def update(self, id: int, data: dict) -> Paciente:
        return super().update(id, data)