from sqlite3 import connect, Connection, Cursor


class Database:
    """ Singleton Database Connection """
    _instance: "Database" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = connect("nosocomio.db")
        return cls._instance

    @classmethod
    def get_connection(cls) -> Connection:
        return cls._instance.connection

    @classmethod
    def open_cursor(cls) -> Cursor:
        return cls.get_connection().cursor()

    @classmethod
    def close_connection(cls):
        if cls._instance is not None:
            cls._instance.connection.close()

    @classmethod
    def commit(cls):
        cls.get_connection().commit()

    @classmethod
    def rollback(cls):
        cls.get_connection().rollback()

    @classmethod
    def execute(cls, query: str, params: tuple = (), single: bool = False) -> Cursor:
        with cls.open_cursor() as cursor:
            cursor.execute(query, params)
            cls.commit()
            if single:
                return cursor.fetchone()
            return cursor.fetchall()
