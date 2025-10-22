import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict

from dao.managers import HabitacionManager, Habitacion
from dao.objetos import tipos_habitacion as TH
from tk_src.base_abm import BaseABMFrame

class ABMHabitacionesFrame(BaseABMFrame):
    def __init__(self, master=None, titulo: str = "Habitación"):
        # mapa tipo -> capacidad sugerida
        self._tipos_map: Dict[str, int] = self._build_tipos_map()
        super().__init__(master, titulo=titulo)

    @property
    def manager(self):
        return HabitacionManager

    def _build_tipos_map(self) -> Dict[str, int]:
        tipos: Dict[str, int] = {}
        for nombre in dir(TH):
            val = getattr(TH, nombre)
            if hasattr(val, "tipo") and hasattr(val, "capacidad"):
                tipos[val.tipo] = int(val.capacidad)
        return tipos

    # --------- Formulario ---------
    def definir_campos_form(self) -> None:
        # id (solo en edición)
        self.variables_por_campo["id"] = tk.StringVar()
        lbl_id = ttk.Label(self.frm_form, text="ID")
        ent_id = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["id"], state="disabled", width=12)
        lbl_id.grid(row=0, column=0, sticky="w", padx=(6,8), pady=4)
        ent_id.grid(row=0, column=1, sticky="w", padx=(0,6), pady=4)
        self.labels_por_campo["id"] = lbl_id
        self.inputs_por_campo["id"] = ent_id
        lbl_id.grid_remove(); ent_id.grid_remove()

        # número
        self.variables_por_campo["numero"] = tk.StringVar()
        ttk.Label(self.frm_form, text="Número").grid(row=1, column=0, sticky="w", padx=(6,8), pady=4)
        ent_numero = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["numero"])
        ent_numero.grid(row=1, column=1, sticky="ew", padx=(0,6), pady=4)
        self.inputs_por_campo["numero"] = ent_numero

        # tipo (combobox)
        self.variables_por_campo["tipo"] = tk.StringVar()
        ttk.Label(self.frm_form, text="Tipo").grid(row=2, column=0, sticky="w", padx=(6,8), pady=4)
        self.cmb_tipo = ttk.Combobox(self.frm_form, state="readonly", textvariable=self.variables_por_campo["tipo"])
        self.cmb_tipo["values"] = sorted(self._tipos_map.keys())
        self.cmb_tipo.grid(row=2, column=1, sticky="ew", padx=(0,6), pady=4)
        self.cmb_tipo.bind("<<ComboboxSelected>>", self._on_tipo_change)
        self.inputs_por_campo["tipo"] = self.cmb_tipo
        
        # capacidad
        self.variables_por_campo["capacidad"] = tk.StringVar()
        ttk.Label(self.frm_form, text="Capacidad").grid(row=3, column=0, sticky="w", padx=(6,8), pady=4)
        ent_capacidad = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["capacidad"])
        ent_capacidad.grid(row=3, column=1, sticky="ew", padx=(0,6), pady=4)
        self.inputs_por_campo["capacidad"] = ent_capacidad

        self.frm_form.columnconfigure(1, weight=1)

    def _on_tipo_change(self, _evt=None):
        tipo = self.variables_por_campo["tipo"].get()
        if tipo in self._tipos_map:
            self.variables_por_campo["capacidad"].set(str(self._tipos_map[tipo]))

    def setear_desde_modelo(self, habitacion: Optional[Habitacion]) -> None:
        if habitacion is None:
            for k in ("id","numero","tipo","capacidad"):
                self.variables_por_campo[k].set("")
            # seteo tipo default si existe
            if self.cmb_tipo["values"]:
                self.cmb_tipo.current(0)
                self._on_tipo_change()
            return
        self.variables_por_campo["id"].set(str(habitacion.id))
        self.variables_por_campo["numero"].set(str(habitacion.numero))
        self.variables_por_campo["tipo"].set(habitacion.tipo or "")
        self.variables_por_campo["capacidad"].set(str(habitacion.capacidad))

    def recolectar_para_guardar(self) -> dict:
        numero_str = self.variables_por_campo["numero"].get().strip()
        tipo = self.variables_por_campo["tipo"].get().strip()
        capacidad_str = self.variables_por_campo["capacidad"].get().strip()

        if not numero_str.isdigit():
            raise ValueError("El número debe ser un entero positivo.")
        if not tipo:
            raise ValueError("El tipo es obligatorio.")
        if not capacidad_str.isdigit() or int(capacidad_str) <= 0:
            raise ValueError("La capacidad debe ser un entero positivo.")

        return {"numero": int(numero_str), "tipo": tipo, "capacidad": int(capacidad_str)}

    # --------- Listado ---------
    def columnas_listado(self):
        return [
            {"id": "numero",    "title": "N° Hab.",  "width": 100, "stretch": False, "anchor": "center"},
            {"id": "tipo",      "title": "Tipo",     "width": 220, "stretch": True,  "anchor": "w"},
            {"id": "capacidad", "title": "Capacidad","width": 110, "stretch": False, "anchor": "center"},
        ]

    def mapear_modelo_a_fila(self, habitacion: Habitacion):
        return (habitacion.numero, habitacion.tipo or "", habitacion.capacidad)

    def obtener_id(self, habitacion: Habitacion):
        return habitacion.id
