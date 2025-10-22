import tkinter as tk
from tkinter import ttk
from typing import Optional

from dao.managers import MedicoManager
from dao.objetos import Medico

from tk_src.base_abm import BaseABMFrame

class ABMMedicosFrame(BaseABMFrame):
    @property
    def manager(self):
        return MedicoManager

    # --------- Formulario ---------
    def definir_campos_form(self) -> None:
        # id (se muestra solo en edición)
        self.variables_por_campo["id"] = tk.StringVar()
        lbl_id = ttk.Label(self.frm_form, text="ID")
        ent_id = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["id"], state="disabled", width=20)
        lbl_id.grid(row=0, column=0, sticky="w", padx=(6, 8), pady=4)
        ent_id.grid(row=0, column=1, sticky="w", padx=(0, 6), pady=4)
        self.labels_por_campo["id"] = lbl_id
        self.inputs_por_campo["id"] = ent_id

        # nombre
        self.variables_por_campo["nombre"] = tk.StringVar()
        ttk.Label(self.frm_form, text="Nombre").grid(row=1, column=0, sticky="w", padx=(6, 8), pady=4)
        nombre_entry = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["nombre"])
        nombre_entry.grid(row=1, column=1, sticky="ew", padx=(0, 6), pady=4)
        self.inputs_por_campo["nombre"] = nombre_entry

        # matrícula
        self.variables_por_campo["matricula"] = tk.StringVar()
        ttk.Label(self.frm_form, text="Matrícula").grid(row=2, column=0, sticky="w", padx=(6, 8), pady=4)
        matricula_entry = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["matricula"])
        matricula_entry.grid(row=2, column=1, sticky="ew", padx=(0, 6), pady=4)
        self.inputs_por_campo["matricula"] = matricula_entry

        # especialidad
        self.variables_por_campo["especialidad"] = tk.StringVar()
        ttk.Label(self.frm_form, text="Especialidad").grid(row=3, column=0, sticky="w", padx=(6, 8), pady=4)
        especialidad_entry = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["especialidad"])
        especialidad_entry.grid(row=3, column=1, sticky="ew", padx=(0, 6), pady=4)
        self.inputs_por_campo["especialidad"] = especialidad_entry

        # por defecto, ID oculto (en creación)
        self.labels_por_campo["id"].grid_remove()
        self.inputs_por_campo["id"].grid_remove()

        # expandir col 1
        self.frm_form.columnconfigure(1, weight=1)

    def setear_desde_modelo(self, medico: Optional[Medico]) -> None:
        if medico is None:
            self.variables_por_campo["id"].set("")
            self.variables_por_campo["nombre"].set("")
            self.variables_por_campo["matricula"].set("")
            self.variables_por_campo["especialidad"].set("")
            return

        self.variables_por_campo["id"].set(str(medico.id))
        self.variables_por_campo["nombre"].set(medico.nombre or "")
        self.variables_por_campo["matricula"].set("" if medico.matricula is None else str(medico.matricula))
        self.variables_por_campo["especialidad"].set(medico.especialidad or "")

    def recolectar_para_guardar(self) -> dict:
        nombre = self.variables_por_campo["nombre"].get().strip()
        matricula_str = self.variables_por_campo["matricula"].get().strip()
        especialidad = self.variables_por_campo["especialidad"].get().strip()

        if not nombre:
            raise ValueError("El nombre es obligatorio.")
        if not matricula_str.isdigit():
            raise ValueError("La matrícula debe ser numérica entera.")
        matricula = int(matricula_str)

        return {"nombre": nombre, "matricula": matricula, "especialidad": especialidad}

    # --------- Listado (Treeview) ---------
    def columnas_listado(self) -> list[dict]:
        return [
            {"id": "nombre",       "title": "Nombre",       "width": 220, "stretch": True,  "anchor": "w"},
            {"id": "matricula",    "title": "Matrícula",    "width": 120, "stretch": False, "anchor": "center"},
            {"id": "especialidad", "title": "Especialidad", "width": 180, "stretch": True,  "anchor": "w"},
        ]

    def mapear_modelo_a_fila(self, medico: Medico) -> tuple:
        return (medico.nombre or "", medico.matricula if medico.matricula is not None else "", medico.especialidad or "")

    def obtener_id(self, medico: Medico) -> int:
        return medico.id
