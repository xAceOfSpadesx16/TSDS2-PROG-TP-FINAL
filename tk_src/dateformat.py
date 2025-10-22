from __future__ import annotations
from datetime import datetime

UI_DATETIME_FMT = "%d/%m/%Y %H:%M"
UI_DATE_FMT = "%d/%m/%Y"

def to_ui_datetime(dt: datetime | None) -> str:
    """Formatea datetime a 'dd/mm/YYYY HH:MM' (o devuelve '')."""
    return dt.strftime(UI_DATETIME_FMT) if isinstance(dt, datetime) else ""

def now_ui_string() -> str:
    """Devuelve 'ahora' en formato UI."""
    return datetime.now().replace(second=0, microsecond=0).strftime(UI_DATETIME_FMT)

def parse_ui_datetime_strict(s: str) -> datetime:
    """
    Parse estricto de 'dd/mm/YYYY HH:MM' para campos de ingreso/alta.
    Lanza ValueError si no coincide.
    """
    s = (s or "").strip()
    return datetime.strptime(s, UI_DATETIME_FMT)

def parse_ui_date_or_datetime(s: str) -> datetime:
    """
    Para filtros: acepta 'dd/mm/YYYY' o 'dd/mm/YYYY HH:MM'.
    Si viene solo fecha, devuelve ese día a las 00:00.
    """
    s = (s or "").strip()
    try:
        return datetime.strptime(s, UI_DATETIME_FMT)
    except ValueError:
        # intenta solo fecha → 00:00
        return datetime.strptime(s, UI_DATE_FMT)
