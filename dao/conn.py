# conn.py
from sqlite3 import connect, Connection

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
    def close_connection(cls) -> None:
        if cls._instance is not None:
            cls._instance.connection.close()

    @classmethod
    def commit(cls) -> None:
        cls.get_connection().commit()

    @classmethod
    def rollback(cls) -> None:
        cls.get_connection().rollback()

    @classmethod
    def get_execute(cls, query: str, params: tuple = (), single: bool = False) -> list | tuple | None:
        cursor = cls.get_connection().cursor()
        cursor.execute(query, params)
        result = cursor.fetchone() if single else cursor.fetchall()
        cursor.close()
        return result

    @classmethod
    def save_execute(cls, query: str, params: tuple = ()) -> int:
        cursor = cls.get_connection().cursor()
        cursor.execute(query, params)
        cls.commit()
        sql = query.lstrip().upper()
        if sql.startswith("INSERT"):
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        else:
            rowcount = cursor.rowcount
            cursor.close()
            return rowcount
