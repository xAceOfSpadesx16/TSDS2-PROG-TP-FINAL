from __future__ import annotations
# informes.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, Optional, Sequence

from tk_src.table_view import SimpleTable
from tk_src import dateformat
from dao.managers import (
    MovimientoManager,
    MedicoManager,
    PacienteManager,
    CamaManager,
    HabitacionManager,
)

class InformesFrame(ttk.Frame):
    """
    Informes solicitados:
    - Camas ocupadas hoy (detalle)
    - Ingresados por médico
    - Ingresados entre fechas
    - Altas entre fechas
    - Pacientes con más de un ingreso
    - Total internados hoy
    - Médicos ordenados por {id, nombre, especialidad}
    Usa Managers/Models; sin SQL directo ni imports innecesarios.
    """
    def __init__(self, master=None):
        super().__init__(master, padding=12, style="Card.TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # caches simples para evitar reconsultas
        self._pac_cache: Dict[int, str] = {}
        self._hab_cache: Dict[int, tuple[int, str, int]]  = {}  # id -> (numero, tipo, capacidad)
        self._cama_hab_cache: Dict[int, int] = {}  # cama_id -> habitacion_id

        nb = ttk.Notebook(self)
        nb.grid(row=0, column=0, sticky="nsew")

        self._build_tab_camas_ocupadas(nb)
        self._build_tab_ingresos_medico(nb)
        self._build_tab_ingresos_entre(nb)
        self._build_tab_altas_entre(nb)
        self._build_tab_multiples(nb)
        self._build_tab_medicos_orden(nb)

    # -------------------- helpers --------------------
    def _show_error(self, e: Exception) -> None:
        messagebox.showerror("Error", (str(e).strip() or e.__class__.__name__))

    def _parse_fecha(self, s: str) -> datetime:
        # dd/mm/YYYY o dd/mm/YYYY HH:MM
        return dateformat.parse_ui_date_or_datetime(s)

    def _paciente_nombre(self, paciente_id: int) -> str:
        if paciente_id not in self._pac_cache:
            p = PacienteManager.get_one(paciente_id)
            self._pac_cache[paciente_id] = (p.nombre if p else "-")
        return self._pac_cache[paciente_id]

    def _habitacion_info(self, habitacion_id: int) -> tuple[int, str, int]:
        """Devuelve (numero, tipo, capacidad)"""
        if habitacion_id not in self._hab_cache:
            h = HabitacionManager.get_one(habitacion_id)
            self._hab_cache[habitacion_id] = (h.numero, h.tipo, h.capacidad) if h else (-1, "-", 0)
        return self._hab_cache[habitacion_id]

    def _hab_de_cama(self, cama_id: int) -> int:
        if cama_id not in self._cama_hab_cache:
            c = CamaManager.get_one(cama_id)
            self._cama_hab_cache[cama_id] = c.habitacion_id if c else -1
        return self._cama_hab_cache[cama_id]

    # ==================== Camas ocupadas hoy ====================
    def _build_tab_camas_ocupadas(self, nb: ttk.Notebook) -> None:
        tab = ttk.Frame(nb, padding=8, style="Card.TFrame")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        header = ttk.Frame(tab, style="Card.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        for c in range(3):
            header.columnconfigure(c, weight=1, uniform="hdr")

        # 2) Labels centrados en su columna (sticky='ew' + anchor='center')
        self.lbl_camas_count = ttk.Label(header, text="Camas ocupadas: 0", anchor="center")
        self.lbl_camas_count.grid(row=0, column=0, sticky="ew")

        self.lbl_total = ttk.Label(header, text="Internados hoy: 0", anchor="center")
        self.lbl_total.grid(row=0, column=1, sticky="ew")

        # 3) Botón centrado en su columna y refresco de ambos contadores
        ttk.Button(
            header,
            text="Refrescar",
            style="Ghost.TButton",
            command=self._refresh_camas_header
        ).grid(row=0, column=2)  # sin sticky => queda centrado

        cols = [
            {"id": "paciente", "title": "Paciente", "width": 220, "stretch": True, "anchor": "w"},
            {"id": "medico", "title": "Médico", "width": 200, "stretch": True, "anchor": "w"},
            {"id": "habitacion", "title": "Habitación", "width": 120, "stretch": False, "anchor": "center"},
            {"id": "cama", "title": "Cama", "width": 80, "stretch": False, "anchor": "center"},
            {"id": "ingreso", "title": "Ingreso", "width": 160, "stretch": False, "anchor": "center"},
            {"id": "mid", "title": "ID Mov.", "width": 90, "stretch": False, "anchor": "center"},
        ]
        self.tbl_camas = SimpleTable(tab, columns=cols)
        self.tbl_camas.grid(row=1, column=0, sticky="nsew")

        nb.add(tab, text="Camas ocupadas")

        # 4) Cargar ambos contadores al iniciar la pestaña
        self._refresh_camas_header()

    def _refresh_camas_header(self) -> None:
        self._load_camas_ocupadas()
        self._load_total()

    def _load_camas_ocupadas(self) -> None:
        filas = MovimientoManager.detalle_camas_ocupadas()
        self.lbl_camas_count.configure(text=f"Camas ocupadas: {len(filas)}")
        self.tbl_camas.set_rows(
            filas,
            iid_getter=lambda d: d["movimiento_id"],
            values_getter=lambda d: (
                d.get("paciente","-"),
                d.get("medico","-"),
                d.get("habitacion_numero","-"),
                d.get("cama_id","-"),
                dateformat.to_ui_datetime(d.get("fecha_ingreso")),
                d.get("movimiento_id","-"),
            )
        )

    # ==================== Ingresados por médico ====================
    def _build_tab_ingresos_medico(self, nb: ttk.Notebook) -> None:
        tab = ttk.Frame(nb, padding=8, style="Card.TFrame")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        top = ttk.Frame(tab, style="Card.TFrame")
        top.grid(row=0, column=0, sticky="ew", pady=(0,6))
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="Médico").grid(row=0, column=0, sticky="w", padx=(4,8))
        self._map_med_label_to_id: Dict[str, int] = {}
        self.cmb_med = ttk.Combobox(top, state="readonly")
        self.cmb_med.grid(row=0, column=1, sticky="ew")
        ttk.Button(top, text="Buscar", style="Accent.TButton", command=self._buscar_ingresos_medico)\
            .grid(row=0, column=2, padx=(8,0))

        cols = [
            {"id": "paciente","title":"Paciente","width":220,"stretch":True,"anchor":"w"},
            {"id": "hab","title":"Hab.","width":80,"stretch":False,"anchor":"center"},
            {"id": "cama","title":"Cama","width":80,"stretch":False,"anchor":"center"},
            {"id": "ingreso","title":"Ingreso","width":160,"stretch":False,"anchor":"center"},
            {"id": "alta","title":"Alta","width":160,"stretch":False,"anchor":"center"},
            {"id": "mid","title":"ID Mov.","width":90,"stretch":False,"anchor":"center"},
        ]
        self.tbl_ing_med = SimpleTable(tab, columns=cols)
        self.tbl_ing_med.grid(row=1, column=0, sticky="nsew")

        nb.add(tab, text="Ingresos por médico")
        self._load_medicos_combo()

    def _load_medicos_combo(self) -> None:
        self._map_med_label_to_id.clear()
        labels = []
        for medico in MedicoManager.listar_ordenado("nombre"):
            label = f"{medico.id} – {medico.nombre} (Mat {medico.matricula})"
            self._map_med_label_to_id[label] = medico.id
            labels.append(label)
        self.cmb_med["values"] = labels
        if labels:
            self.cmb_med.current(0)

    def _buscar_ingresos_medico(self) -> None:
        if not self.cmb_med.get():
            return
        medico_id = self._map_med_label_to_id[self.cmb_med.get()]
        movimientos = MovimientoManager.ingresados_por_medico(medico_id)

        from dao.objetos import Movimiento
        def get_row_values(movimiento: Movimiento) -> tuple[str, int, int, str, str, int]:
            paciente: str = self._paciente_nombre(movimiento.paciente_id)
            habitacion_id: int = self._hab_de_cama(movimiento.cama_id)
            numero, tipo, capacidad = self._habitacion_info(habitacion_id) if habitacion_id != -1 else ("-","-",0)
            return (
                paciente,
                numero if isinstance(numero, int) else numero,
                movimiento.cama_id,
                dateformat.to_ui_datetime(movimiento.fecha_ingreso),
                dateformat.to_ui_datetime(movimiento.fecha_egreso),
                movimiento.id
            )

        self.tbl_ing_med.set_rows(movimientos, iid_getter=lambda movimiento: movimiento.id, values_getter=get_row_values)

    # ==================== Ingresados entre fechas ====================
    def _build_tab_ingresos_entre(self, nb: ttk.Notebook) -> None:
        tab = ttk.Frame(nb, padding=8, style="Card.TFrame")
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(1, weight=1)

        top = ttk.Frame(tab, style="Card.TFrame")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,6))
        for c in (1,3): top.columnconfigure(c, weight=1)

        ttk.Label(top, text="Desde").grid(row=0, column=0, sticky="w", padx=(4,8))
        desde_entry = ttk.Entry(top)
        desde_entry.grid(row=0, column=1, sticky="ew")
        self.desde_entry = desde_entry

        ttk.Label(top, text="Hasta").grid(row=0, column=2, sticky="w", padx=(8,8))
        hasta_entry = ttk.Entry(top)
        hasta_entry.grid(row=0, column=3, sticky="ew")
        self.hasta_entry = hasta_entry

        ttk.Button(top, text="Buscar", style="Accent.TButton", command=self._buscar_ingresos_entre)\
            .grid(row=0, column=4, padx=(8,0))

        cols = [
            {"id":"paciente","title":"Paciente","width":220,"stretch":True,"anchor":"w"},
            {"id":"medico","title":"Médico","width":200,"stretch":True,"anchor":"w"},
            {"id":"hab","title":"Hab.","width":80,"stretch":False,"anchor":"center"},
            {"id":"cama","title":"Cama","width":80,"stretch":False,"anchor":"center"},
            {"id":"ingreso","title":"Ingreso","width":160,"stretch":False,"anchor":"center"},
            {"id":"mid","title":"ID Mov.","width":90,"stretch":False,"anchor":"center"},
        ]
        self.tbl_ing_entre = SimpleTable(tab, columns=cols)
        self.tbl_ing_entre.grid(row=1, column=0, columnspan=2, sticky="nsew")

        nb.add(tab, text="Ingresos entre fechas")

    def _buscar_ingresos_entre(self) -> None:
        try:
            fecha_desde = self._parse_fecha(self.desde_entry.get())
            fecha_hasta = self._parse_fecha(self.hasta_entry.get())
        except Exception as e:
            self._show_error(e)
            return
        movimientos = MovimientoManager.ingresados_entre(fecha_desde, fecha_hasta)

        from dao.objetos import Movimiento
        def get_row_values(movimiento: Movimiento) -> tuple[str, str, int | str, int, str, int]:
            paciente: str = self._paciente_nombre(movimiento.paciente_id)
            medico = MedicoManager.get_one(movimiento.medico_id)
            habitacion_id = self._hab_de_cama(movimiento.cama_id)
            numero, tipo, capacidad = self._habitacion_info(habitacion_id) if habitacion_id != -1 else ("-","-",0)
            return (
                paciente,
                (medico.nombre if medico else "-"),
                numero,
                movimiento.cama_id,
                dateformat.to_ui_datetime(movimiento.fecha_ingreso),
                movimiento.id
            )

        self.tbl_ing_entre.set_rows(movimientos, iid_getter=lambda movimiento: movimiento.id, values_getter=get_row_values)

    # ==================== Altas entre fechas ====================
    def _build_tab_altas_entre(self, nb: ttk.Notebook) -> None:
        tab = ttk.Frame(nb, padding=8, style="Card.TFrame")
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(1, weight=1)

        top = ttk.Frame(tab, style="Card.TFrame")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,6))
        for c in (1,3): top.columnconfigure(c, weight=1)

        ttk.Label(top, text="Desde").grid(row=0, column=0, sticky="w", padx=(4,8))
        alt_desde_entry = ttk.Entry(top)
        alt_desde_entry.grid(row=0, column=1, sticky="ew")
        self.alt_desde_entry = alt_desde_entry

        ttk.Label(top, text="Hasta").grid(row=0, column=2, sticky="w", padx=(8,8))
        alt_hasta_entry = ttk.Entry(top)
        alt_hasta_entry.grid(row=0, column=3, sticky="ew")
        self.alt_hasta_entry = alt_hasta_entry

        ttk.Button(top, text="Buscar", style="Accent.TButton", command=self._buscar_altas_entre)\
            .grid(row=0, column=4, padx=(8,0))

        cols = [
            {"id":"paciente","title":"Paciente","width":220,"stretch":True,"anchor":"w"},
            {"id":"medico","title":"Médico","width":200,"stretch":True,"anchor":"w"},
            {"id":"hab","title":"Hab.","width":80,"stretch":False,"anchor":"center"},
            {"id":"cama","title":"Cama","width":80,"stretch":False,"anchor":"center"},
            {"id":"ingreso","title":"Ingreso","width":160,"stretch":False,"anchor":"center"},
            {"id":"alta","title":"Alta","width":160,"stretch":False,"anchor":"center"},
            {"id":"mid","title":"ID Mov.","width":90,"stretch":False,"anchor":"center"},
        ]
        self.tbl_alt_entre = SimpleTable(tab, columns=cols)
        self.tbl_alt_entre.grid(row=1, column=0, columnspan=2, sticky="nsew")

        nb.add(tab, text="Altas entre fechas")

    def _buscar_altas_entre(self) -> None:
        try:
            fecha_desde = self._parse_fecha(self.alt_desde_entry.get())
            fecha_hasta = self._parse_fecha(self.alt_hasta_entry.get())
        except Exception as e:
            self._show_error(e)
            return
        movimientos = MovimientoManager.altas_entre(fecha_desde, fecha_hasta)

        from dao.objetos import Movimiento
        def get_row_values(movimiento: Movimiento) -> tuple[str, str, int | str, int, str, str, int]:
            paciente: str = self._paciente_nombre(movimiento.paciente_id)
            medico = MedicoManager.get_one(movimiento.medico_id)
            habitacion_id = self._hab_de_cama(movimiento.cama_id)
            numero, tipo, capacidad = self._habitacion_info(habitacion_id) if habitacion_id != -1 else ("-","-",0)
            return (
                paciente,
                (medico.nombre if medico else "-"),
                numero,
                movimiento.cama_id,
                dateformat.to_ui_datetime(movimiento.fecha_ingreso),
                dateformat.to_ui_datetime(movimiento.fecha_egreso),
                movimiento.id
            )
        self.tbl_alt_entre.set_rows(movimientos, iid_getter=lambda movimiento: movimiento.id, values_getter=get_row_values)

    # ==================== Pacientes con múltiples ingresos ====================
    def _build_tab_multiples(self, nb: ttk.Notebook) -> None:
        tab = ttk.Frame(nb, padding=8, style="Card.TFrame")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        top = ttk.Frame(tab, style="Card.TFrame")
        top.grid(row=0, column=0, sticky="ew", pady=(0,6))
        ttk.Button(top, text="Refrescar", style="Ghost.TButton", command=self._load_multiples)\
            .grid(row=0, column=0, sticky="w")

        cols = [
            {"id":"paciente","title":"Paciente","width":260,"stretch":True,"anchor":"w"},
            {"id":"cantidad","title":"Ingresos","width":120,"stretch":False,"anchor":"center"},
        ]
        self.tbl_mult = SimpleTable(tab, columns=cols)
        self.tbl_mult.grid(row=1, column=0, sticky="nsew")

        nb.add(tab, text="Múltiples ingresos")
        self._load_multiples()

    def _load_multiples(self) -> None:
        multiples_ingresos = MovimientoManager.pacientes_con_multiples_ingresos() 
        filas: list[dict[str, int | str]] = []
        for paciente_id, cantidad in multiples_ingresos:
            filas.append({"paciente": self._paciente_nombre(paciente_id), "cantidad": cantidad, "iid": paciente_id})
        self.tbl_mult.set_rows(
            filas,
            iid_getter=lambda fila: fila["iid"],
            values_getter=lambda fila: (fila["paciente"], fila["cantidad"])
        )

    # ==================== Total internados hoy ====================

    def _load_total(self) -> None:
        n = MovimientoManager.total_internados_hoy()
        self.lbl_total.configure(text=f"Internados hoy: {n}")

    # ==================== Médicos ordenados ====================
    def _build_tab_medicos_orden(self, nb: ttk.Notebook) -> None:
        tab = ttk.Frame(nb, padding=8, style="Card.TFrame")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        top = ttk.Frame(tab, style="Card.TFrame")
        top.grid(row=0, column=0, sticky="ew", pady=(0,6))

        self._orden_var = tk.StringVar(value="id")
        for i, (label, val) in enumerate((("ID","id"), ("Nombre","nombre"), ("Especialidad","especialidad"))):
            ttk.Radiobutton(top, text=label, value=val, variable=self._orden_var).grid(row=0, column=i, padx=6)

        ttk.Button(top, text="Ordenar", style="Accent.TButton", command=self._load_medicos_orden)\
            .grid(row=0, column=3, padx=(12,0))

        cols = [
            {"id":"id","title":"ID","width":80,"stretch":False,"anchor":"center"},
            {"id":"nombre","title":"Nombre","width":220,"stretch":True,"anchor":"w"},
            {"id":"matricula","title":"Matrícula","width":120,"stretch":False,"anchor":"center"},
            {"id":"especialidad","title":"Especialidad","width":200,"stretch":True,"anchor":"w"},
        ]
        self.tbl_med_ord = SimpleTable(tab, columns=cols)
        self.tbl_med_ord.grid(row=1, column=0, sticky="nsew")

        nb.add(tab, text="Médicos ordenados")
        self._load_medicos_orden()

    def _load_medicos_orden(self) -> None:
        criterio = self._orden_var.get()
        medicos = MedicoManager.listar_ordenado(criterio)
        self.tbl_med_ord.set_rows(
            medicos,
            iid_getter=lambda m: m.id,
            values_getter=lambda m: (m.id, m.nombre or "", m.matricula if m.matricula is not None else "", m.especialidad or "")
        )

    # -------------------- integración externa --------------------
    def refrescar(self) -> None:
        """Llamada desde el Notebook principal al cambiar a esta pestaña."""
        # Se refrescan informes rápidos
        self._load_camas_ocupadas()
        self._load_total()
    # -------------------- integración externa --------------------
    def refrescar(self) -> None:
        """Llamada desde el Notebook principal al cambiar a esta pestaña."""
        # Se refrescan informes rápidos
        self._load_camas_ocupadas()
        self._load_total()
