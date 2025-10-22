# managers.py
from typing import TypeVar, Generic, Type, Optional, Iterable
from datetime import datetime
from dao.conn import Database
from dao.objetos import Paciente, Medico, Habitacion, Movimiento, Cama, BaseModel

ModelType = TypeVar('ModelType', bound=BaseModel)

class SQLBuilder:
    @staticmethod
    def build_insert_query(table_name: str, keys: tuple[str, ...]) -> str:
        placeholders = ", ".join("?" for _ in keys[1:])
        columns = ", ".join(keys[1:])
        return f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    @staticmethod
    def build_select_query(table_name: str, keys: tuple[str, ...], conditions: dict = None) -> str:
        base_query = f"SELECT {', '.join(keys)} FROM {table_name}"
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

    @staticmethod
    def create_table_query(table_name: str, keys: tuple[str, ...], types: tuple[str, ...]) -> str:
        columns = ", ".join(f"{key} {type_}" for key, type_ in zip(keys, types))
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"


class BaseManager(Generic[ModelType]):
    model: Type[ModelType]
    conn: Database = Database()
    keys: tuple[str, ...]
    key_types: tuple[str, ...]
    table_name: str

    # ---------- helpers ----------
    @classmethod
    def _crear_desde_fila(cls, fila: Iterable) -> ModelType:
        datos = dict(zip(cls.keys, fila))
        return cls.create_object(datos)

    @classmethod
    def _normalizar_para_guardar(cls, data: dict) -> tuple:
        valores = []
        for key in cls.keys[1:]:
            valor = data.get(key)
            # Normalización mínima para datetime -> ISO
            if isinstance(valor, datetime):
                valor = valor.isoformat()
            valores.append(valor)
        return tuple(valores)

    @classmethod
    def create_object(cls, data: dict) -> ModelType:
        return cls.model(**data)

    # ---------- CRUD ----------
    @classmethod
    def create(cls, data: dict) -> ModelType:
        query = SQLBuilder.build_insert_query(cls.table_name, cls.keys)
        valores = cls._normalizar_para_guardar(data)
        nuevo_id = cls.conn.save_execute(query, valores)
        return cls.get_one(nuevo_id)

    @classmethod
    def get_one(cls, id: int) -> Optional[ModelType]:
        query = SQLBuilder.build_select_query(cls.table_name, cls.keys, {"id": id})
        fila = cls.conn.get_execute(query, (id,), single=True)
        if fila is None:
            return None
        return cls._crear_desde_fila(fila)

    @classmethod
    def get_list(cls) -> list[ModelType]:
        query = SQLBuilder.build_select_query(cls.table_name, cls.keys)
        filas = cls.conn.get_execute(query)
        return [cls._crear_desde_fila(f) for f in filas]

    @classmethod
    def filter(cls, **kwargs) -> list[ModelType]:
        params = tuple(kwargs.values())
        query = SQLBuilder.build_select_query(cls.table_name, cls.keys, kwargs)
        filas = cls.conn.get_execute(query, params)
        return [cls._crear_desde_fila(f) for f in filas]

    @classmethod
    def update(cls, id: int, data: dict) -> Optional[ModelType]:
        query = SQLBuilder.build_update_query(cls.table_name, cls.keys)
        valores = []
        for key in cls.keys:
            if key == "id": 
                continue
            valor = data.get(key)
            if isinstance(valor, datetime):
                valor = valor.isoformat()
            valores.append(valor)
        cls.conn.save_execute(query, tuple(valores) + (id,))
        return cls.get_one(id)

    @classmethod
    def delete(cls, id: int) -> None:
        query = SQLBuilder.build_delete_query(cls.table_name)
        cls.conn.save_execute(query, (id,))

    @classmethod
    def create_table(cls) -> None:
        query = SQLBuilder.create_table_query(cls.table_name, cls.keys, cls.key_types)
        cls.conn.save_execute(query)


# ----------------- Managers concretos -----------------

class PacienteManager(BaseManager[Paciente]):
    model = Paciente
    keys = ("id", "nombre", "obra_social", "numero_afiliado", "domicilio", "telefono")
    key_types = ("INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT")
    table_name = "pacientes"

class MedicoManager(BaseManager[Medico]):
    model = Medico
    keys = ("id", "nombre", "matricula", "especialidad")
    key_types = ("INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT", "INTEGER", "TEXT")
    table_name = "medicos"

    @classmethod
    def _existe_matricula(cls, matricula: int, excluir_id: int | None = None) -> bool:
        if excluir_id is None:
            q, p = "SELECT 1 FROM medicos WHERE matricula = ? LIMIT 1", (matricula,)
        else:
            q, p = "SELECT 1 FROM medicos WHERE matricula = ? AND id <> ? LIMIT 1", (matricula, excluir_id)
        return cls.conn.get_execute(q, p, single=True) is not None

    @classmethod
    def listar_ordenado(cls, criterio: str) -> list[Medico]:
        if criterio not in {"id", "nombre", "especialidad"}:
            criterio = "id"
        query = f"SELECT {', '.join(cls.keys)} FROM {cls.table_name} ORDER BY {criterio} ASC"
        filas = cls.conn.get_execute(query)
        return [cls._crear_desde_fila(f) for f in filas]

    @classmethod
    def create(cls, data: dict):
        if cls._existe_matricula(int(data["matricula"])):
            raise ValueError("La matrícula ya existe.")
        return super().create(data)

    @classmethod
    def update(cls, id: int, data: dict):
        if "matricula" in data and cls._existe_matricula(int(data["matricula"]), excluir_id=id):
            raise ValueError("La matrícula ya existe.")
        return super().update(id, data)

    @classmethod
    def create_table(cls) -> None:
        super().create_table()
        cls.conn.save_execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_medicos_matricula ON medicos(matricula)")

class HabitacionManager(BaseManager[Habitacion]):
    model = Habitacion
    keys = ("id", "numero", "tipo", "capacidad")
    key_types = ("INTEGER PRIMARY KEY AUTOINCREMENT", "INTEGER", "TEXT", "INTEGER")
    table_name = "habitaciones"

class CamaManager(BaseManager[Cama]):
    model = Cama
    keys = ("id", "habitacion_id")
    key_types = ("INTEGER PRIMARY KEY AUTOINCREMENT", "INTEGER")
    table_name = "camas"

    @classmethod
    def esta_ocupada(cls, cama_id: int) -> bool:
        q = "SELECT 1 FROM movimientos WHERE cama_id = ? AND fecha_egreso IS NULL LIMIT 1"
        fila = cls.conn.get_execute(q, (cama_id,), single=True)
        return fila is not None

    @classmethod
    def camas_libres(cls) -> list[Cama]:
        q = """
            SELECT c.id, c.habitacion_id
            FROM camas c
            WHERE c.id NOT IN (SELECT cama_id FROM movimientos WHERE fecha_egreso IS NULL)
            ORDER BY c.id
        """
        filas = cls.conn.get_execute(q)
        return [cls._crear_desde_fila(f) for f in filas]

    @classmethod
    def contar_en_habitacion(cls, habitacion_id: int) -> int:
        return len(cls.filter(habitacion_id=habitacion_id))

    @classmethod
    def create(cls, data: dict) -> Cama:
        habitacion_id = int(data["habitacion_id"])
        habitacion = HabitacionManager.get_one(habitacion_id)
        if habitacion is None:
            raise ValueError("Habitación inexistente.")
        actuales = cls.contar_en_habitacion(habitacion_id)
        if actuales >= habitacion.capacidad:
            raise ValueError("La habitación ya alcanzó su capacidad de camas.")
        return super().create(data)

    @classmethod
    def update(cls, id: int, data: dict) -> Cama:
        # si cambian la habitación, validar capacidad
        if "habitacion_id" in data:
            nueva_hab = int(data["habitacion_id"])
            actual = cls.get_one(id)
            if actual is None:
                raise ValueError("Cama inexistente.")
            if nueva_hab != actual.habitacion_id:
                habitacion = HabitacionManager.get_one(nueva_hab)
                if habitacion is None:
                    raise ValueError("Habitación inexistente.")
                actuales = cls.contar_en_habitacion(nueva_hab)
                if actuales >= habitacion.capacidad:
                    raise ValueError("La habitación ya alcanzó su capacidad de camas.")
        return super().update(id, data)

    @classmethod
    def delete(cls, id: int) -> None:
        if cls.esta_ocupada(id):
            raise ValueError("No se puede eliminar una cama ocupada.")
        return super().delete(id)

class MovimientoManager(BaseManager[Movimiento]):
    model = Movimiento
    keys = ("id", "cama_id", "paciente_id", "medico_id", "fecha_ingreso", "fecha_egreso")
    key_types = ("INTEGER PRIMARY KEY AUTOINCREMENT", "INTEGER", "INTEGER", "INTEGER", "TEXT", "TEXT")
    table_name = "movimientos"

    # --- override para parsear fechas al leer ---
    @classmethod
    def _crear_desde_fila(cls, fila):
        datos = dict(zip(cls.keys, fila))
        # parseo ISO -> datetime / None
        fi = datos.get("fecha_ingreso")
        fe = datos.get("fecha_egreso")
        datos["fecha_ingreso"] = datetime.fromisoformat(fi) if isinstance(fi, str) else fi
        datos["fecha_egreso"] = datetime.fromisoformat(fe) if isinstance(fe, str) and fe else None
        return cls.create_object(datos)

    # ---------- reglas de negocio ----------
    @classmethod
    def tiene_internacion_abierta(cls, paciente_id: int) -> bool:
        q = "SELECT 1 FROM movimientos WHERE paciente_id = ? AND fecha_egreso IS NULL LIMIT 1"
        fila = cls.conn.get_execute(q, (paciente_id,), single=True)
        return fila is not None

    @classmethod
    def ingresar(cls, *, cama_id: int, paciente_id: int, medico_id: int, fecha_ingreso: datetime) -> Movimiento:
        # Validaciones requeridas por el enunciado
        if CamaManager.esta_ocupada(cama_id):
            raise ValueError("La cama seleccionada está ocupada.")
        if cls.tiene_internacion_abierta(paciente_id):
            raise ValueError("El paciente ya tiene una internación abierta.")
        data = {
            "id": 0,
            "cama_id": cama_id,
            "paciente_id": paciente_id,
            "medico_id": medico_id,
            "fecha_ingreso": fecha_ingreso,
            "fecha_egreso": None
        }
        return cls.create(data)

    @classmethod
    def dar_alta(cls, movimiento_id: int, fecha_egreso: datetime) -> Movimiento:
        mov = cls.get_one(movimiento_id)
        if mov is None:
            raise ValueError("Movimiento inexistente.")
        if mov.fecha_egreso is not None:
            raise ValueError("El movimiento ya tiene alta registrada.")
        if fecha_egreso < mov.fecha_ingreso:
            raise ValueError("La fecha de alta no puede ser anterior al ingreso.")
        return cls.update(movimiento_id, {
            "id": movimiento_id,
            "cama_id": mov.cama_id,
            "paciente_id": mov.paciente_id,
            "medico_id": mov.medico_id,
            "fecha_ingreso": mov.fecha_ingreso,
            "fecha_egreso": fecha_egreso
        })

    # ---------- consultas para Informes ----------
    @classmethod
    def internaciones_abiertas(cls) -> list[Movimiento]:
        q = f"SELECT {', '.join(cls.keys)} FROM {cls.table_name} WHERE fecha_egreso IS NULL ORDER BY fecha_ingreso"
        filas = cls.conn.get_execute(q)
        return [cls._crear_desde_fila(f) for f in filas]

    @classmethod
    def ingresados_por_medico(cls, medico_id: int) -> list[Movimiento]:
        q = f"SELECT {', '.join(cls.keys)} FROM {cls.table_name} WHERE medico_id = ? ORDER BY fecha_ingreso"
        filas = cls.conn.get_execute(q, (medico_id,))
        return [cls._crear_desde_fila(f) for f in filas]

    @classmethod
    def ingresados_entre(cls, f_ini: datetime, f_fin: datetime) -> list[Movimiento]:
        q = f"""
            SELECT {', '.join(cls.keys)} FROM {cls.table_name}
            WHERE date(fecha_ingreso) BETWEEN date(?) AND date(?)
            ORDER BY fecha_ingreso
        """
        filas = cls.conn.get_execute(q, (f_ini.date().isoformat(), f_fin.date().isoformat()))
        return [cls._crear_desde_fila(f) for f in filas]

    @classmethod
    def altas_entre(cls, f_ini: datetime, f_fin: datetime) -> list[Movimiento]:
        q = f"""
            SELECT {', '.join(cls.keys)} FROM {cls.table_name}
            WHERE fecha_egreso IS NOT NULL
            AND date(fecha_egreso) BETWEEN date(?) AND date(?)
            ORDER BY fecha_egreso
        """
        filas = cls.conn.get_execute(q, (f_ini.date().isoformat(), f_fin.date().isoformat()))
        return [cls._crear_desde_fila(f) for f in filas]

    @classmethod
    def pacientes_con_multiples_ingresos(cls) -> list[tuple[int, int]]:
        # Devuelve lista de (paciente_id, cantidad)
        q = """
            SELECT paciente_id, COUNT(*) AS total
            FROM movimientos
            GROUP BY paciente_id
            HAVING COUNT(*) > 1
            ORDER BY total DESC
        """
        return cls.conn.get_execute(q)

    @classmethod
    def total_internados_hoy(cls) -> int:
        q = "SELECT COUNT(*) FROM movimientos WHERE fecha_egreso IS NULL"
        count = cls.conn.get_execute(q, single=True)
        return count[0] if count else 0

    @classmethod
    def detalle_camas_ocupadas(cls) -> list[dict]:
        q = """
            SELECT m.id,
                p.nombre     AS paciente,
                md.nombre    AS medico,
                h.numero     AS habitacion,
                c.id         AS cama_id,
                m.fecha_ingreso
            FROM movimientos m
            JOIN pacientes   p  ON p.id = m.paciente_id
            JOIN medicos     md ON md.id = m.medico_id
            JOIN camas       c  ON c.id = m.cama_id
            JOIN habitaciones h  ON h.id = c.habitacion_id
            WHERE m.fecha_egreso IS NULL
            ORDER BY h.numero, c.id, m.fecha_ingreso
        """
        filas = cls.conn.get_execute(q)
        out = []
        for mid, pac, med, hab, cid, fin in filas:
            # fin (TEXT ISO) -> datetime
            fi_dt = None
            if isinstance(fin, str):
                try:
                    fi_dt = datetime.fromisoformat(fin)
                except Exception:
                    fi_dt = None
            out.append({
                "movimiento_id": mid,
                "paciente": pac,
                "medico": med,
                "habitacion_numero": hab,
                "cama_id": cid,
                "fecha_ingreso": fi_dt,
            })
        return out