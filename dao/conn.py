from sqlite3 import connect, Connection, Cursor
from typing import ContextManager

class Database:
    """ Singleton Database Connection """

    _instance: "Database" = None
    connection: Connection
    db_file: str = "nosocomio.db"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = connect(cls.db_file)
        return cls._instance

    @classmethod
    def get_connection(cls) -> Connection:
        return cls._instance.connection

    @classmethod
    def close_connection(cls):
        if cls._instance is not None:
            cls._instance.connection.close()
    
    @classmethod
    def open_context_manager_cursor(cls) -> ContextManager[Cursor]:
        return cls.get_connection().cursor()


    @classmethod
    def commit(cls):
        cls.get_connection().commit()

    @classmethod
    def rollback(cls):
        cls.get_connection().rollback()

    @classmethod
    def get_execute(cls, query: str, params: tuple = (), single: bool = False) -> Cursor:
        with cls.open_context_manager_cursor() as cursor:
            cursor.execute(query, params)
            if single:
                return cursor.fetchone()
            return cursor.fetchall()

    @classmethod
    def save_execute(cls, query: str, params: tuple = ()) -> int:
        with cls.open_context_manager_cursor() as cursor:
            cursor.execute(query, params)
            cls.commit()
            return cursor.lastrowid