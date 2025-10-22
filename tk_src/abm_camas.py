# abm_camas.py
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, List

from dao.managers import CamaManager, Cama, HabitacionManager, Habitacion
from tk_src.base_abm import BaseABMFrame

class ABMCamasFrame(BaseABMFrame):
    def __init__(self, master=None, titulo: str = "Cama"):
        self._map_hab_label_to_id: Dict[str, int] = {}
        self._cache_hab: Dict[int, Habitacion] = {}
        super().__init__(master, titulo=titulo)

    @property
    def manager(self):
        return CamaManager

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

        # habitación
        self.variables_por_campo["habitacion_label"] = tk.StringVar()
        ttk.Label(self.frm_form, text="Habitación").grid(row=1, column=0, sticky="w", padx=(6,8), pady=4)
        self.cmb_hab = ttk.Combobox(self.frm_form, state="readonly", textvariable=self.variables_por_campo["habitacion_label"])
        self.cmb_hab.grid(row=1, column=1, sticky="ew", padx=(0,6), pady=4)
        self.inputs_por_campo["habitacion_label"] = self.cmb_hab

        self.frm_form.columnconfigure(1, weight=1)
        self._cargar_habitaciones()

    def _cargar_habitaciones(self) -> None:
        self._map_hab_label_to_id.clear()
        self._cache_hab.clear()
        habitaciones = HabitacionManager.get_list()
        habitacion_labels: List[str] = []
        for habitacion in sorted(habitaciones, key=lambda x: (x.numero, x.id)):
            self._cache_hab[habitacion.id] = habitacion
            label = f"{habitacion.numero} – {habitacion.tipo} (cap {habitacion.capacidad})"
            self._map_hab_label_to_id[label] = habitacion.id
            habitacion_labels.append(label)
        self.cmb_hab["values"] = habitacion_labels
        if habitacion_labels:
            self.cmb_hab.current(0)

    def _habitacion_desde_label(self, label: str) -> Optional[Habitacion]:
        habitacion_id = self._map_hab_label_to_id.get(label)
        return self._cache_hab.get(habitacion_id) if habitacion_id else None

    def setear_desde_modelo(self, cama: Optional[Cama]) -> None:
        if cama is None:
            self.variables_por_campo["id"].set("")
            if self.cmb_hab["values"]:
                self.cmb_hab.current(0)
            else:
                self.cmb_hab.set("")
            return
        self.variables_por_campo["id"].set(str(cama.id))
        habitacion = self._cache_hab.get(cama.habitacion_id) or HabitacionManager.get_one(cama.habitacion_id)
        if habitacion:
            label = f"{habitacion.numero} – {habitacion.tipo} (cap {habitacion.capacidad})"
            if label not in self.cmb_hab["values"]:
                self._cargar_habitaciones()
            self.cmb_hab.set(label)
        else:
            self.cmb_hab.set("")

    def recolectar_para_guardar(self) -> dict:
        label = self.variables_por_campo["habitacion_label"].get()
        habitacion = self._habitacion_desde_label(label)
        if not habitacion:
            raise ValueError("Seleccioná una habitación.")
        return {"habitacion_id": int(habitacion.id)}

    # --------- Listado ---------
    def columnas_listado(self):
        return [
            {"id": "cama",       "title": "Cama",       "width": 100, "stretch": False, "anchor": "center"},
            {"id": "habitacion", "title": "Habitación", "width": 180, "stretch": False, "anchor": "center"},
            {"id": "tipo",       "title": "Tipo",       "width": 220, "stretch": True,  "anchor": "w"},
            {"id": "capacidad",  "title": "Cap.",       "width": 80,  "stretch": False, "anchor": "center"},
        ]

    def mapear_modelo_a_fila(self, cama: Cama):
        habitacion = self._cache_hab.get(cama.habitacion_id) or HabitacionManager.get_one(cama.habitacion_id)
        if habitacion:
            return (cama.id, habitacion.numero, habitacion.tipo or "", habitacion.capacidad)
        return (cama.id, "-", "-", "-")

    def obtener_id(self, cama: Cama):
        return cama.id

    # --------- Integración con Notebook (refresh externo) ---------
    def refrescar(self) -> None:
        self._cargar_habitaciones()
        super().refrescar()
    def refrescar(self) -> None:
        self._cargar_habitaciones()
        super().refrescar()
