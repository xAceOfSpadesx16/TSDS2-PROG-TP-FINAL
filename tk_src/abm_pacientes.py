# abm_pacientes.py
import tkinter as tk
from tkinter import ttk
from typing import Optional

from dao.managers import PacienteManager
from dao.objetos import Paciente
from tk_src.base_abm import BaseABMFrame

class ABMPacientesFrame(BaseABMFrame):
    @property
    def manager(self):
        return PacienteManager

    # --------- Formulario ---------
    def definir_campos_form(self) -> None:
        # id (solo visible en edición)
        self.variables_por_campo["id"] = tk.StringVar()
        lbl_id = ttk.Label(self.frm_form, text="ID")
        ent_id = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["id"], state="disabled", width=20)
        lbl_id.grid(row=0, column=0, sticky="w", padx=(6, 8), pady=4)
        ent_id.grid(row=0, column=1, sticky="w", padx=(0, 6), pady=4)
        self.labels_por_campo["id"] = lbl_id
        self.inputs_por_campo["id"] = ent_id
        # por defecto oculto (en creación)
        lbl_id.grid_remove(); ent_id.grid_remove()

        # nombre
        self.variables_por_campo["nombre"] = tk.StringVar()
        ttk.Label(self.frm_form, text="Nombre").grid(row=1, column=0, sticky="w", padx=(6,8), pady=4)
        nombre_entry = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["nombre"])
        nombre_entry.grid(row=1, column=1, sticky="ew", padx=(0,6), pady=4)
        self.inputs_por_campo["nombre"] = nombre_entry

        # obra_social
        self.variables_por_campo["obra_social"] = tk.StringVar()
        ttk.Label(self.frm_form, text="Obra Social").grid(row=2, column=0, sticky="w", padx=(6,8), pady=4)
        obra_social_entry = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["obra_social"])
        obra_social_entry.grid(row=2, column=1, sticky="ew", padx=(0,6), pady=4)
        self.inputs_por_campo["obra_social"] = obra_social_entry

        # numero_afiliado
        self.variables_por_campo["numero_afiliado"] = tk.StringVar()
        ttk.Label(self.frm_form, text="N° Afiliado").grid(row=3, column=0, sticky="w", padx=(6,8), pady=4)
        numero_afiliado_entry = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["numero_afiliado"])
        numero_afiliado_entry.grid(row=3, column=1, sticky="ew", padx=(0,6), pady=4)
        self.inputs_por_campo["numero_afiliado"] = numero_afiliado_entry

        # domicilio
        self.variables_por_campo["domicilio"] = tk.StringVar()
        ttk.Label(self.frm_form, text="Domicilio").grid(row=4, column=0, sticky="w", padx=(6,8), pady=4)
        domicilio_entry = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["domicilio"])
        domicilio_entry.grid(row=4, column=1, sticky="ew", padx=(0,6), pady=4)
        self.inputs_por_campo["domicilio"] = domicilio_entry

        # telefono
        self.variables_por_campo["telefono"] = tk.StringVar()
        ttk.Label(self.frm_form, text="Teléfono").grid(row=5, column=0, sticky="w", padx=(6,8), pady=4)
        telefono_entry = ttk.Entry(self.frm_form, textvariable=self.variables_por_campo["telefono"])
        telefono_entry.grid(row=5, column=1, sticky="ew", padx=(0,6), pady=4)
        self.inputs_por_campo["telefono"] = telefono_entry

        self.frm_form.columnconfigure(1, weight=1)

    def setear_desde_modelo(self, paciente: Optional[Paciente]) -> None:
        if paciente is None:
            for k in ("id","nombre","obra_social","numero_afiliado","domicilio","telefono"):
                self.variables_por_campo[k].set("")
            return
        self.variables_por_campo["id"].set(str(paciente.id))
        self.variables_por_campo["nombre"].set(paciente.nombre or "")
        self.variables_por_campo["obra_social"].set(paciente.obra_social or "")
        self.variables_por_campo["numero_afiliado"].set(paciente.numero_afiliado or "")
        self.variables_por_campo["domicilio"].set(paciente.domicilio or "")
        self.variables_por_campo["telefono"].set(paciente.telefono or "")

    def recolectar_para_guardar(self) -> dict:
        nombre = self.variables_por_campo["nombre"].get().strip()
        if not nombre:
            raise ValueError("El nombre es obligatorio.")
        return {
            "nombre": nombre,
            "obra_social": self.variables_por_campo["obra_social"].get().strip() or None,
            "numero_afiliado": self.variables_por_campo["numero_afiliado"].get().strip() or None,
            "domicilio": self.variables_por_campo["domicilio"].get().strip() or None,
            "telefono": self.variables_por_campo["telefono"].get().strip() or None,
        }

    # --------- Listado ---------
    def columnas_listado(self) -> list[dict]:
        return [
            {"id": "nombre",          "title": "Nombre",        "width": 220, "stretch": True,  "anchor": "w"},
            {"id": "obra_social",     "title": "Obra Social",   "width": 140, "stretch": False, "anchor": "w"},
            {"id": "numero_afiliado", "title": "N° Afiliado",   "width": 120, "stretch": False, "anchor": "center"},
            {"id": "telefono",        "title": "Teléfono",      "width": 120, "stretch": False, "anchor": "center"},
        ]

    def mapear_modelo_a_fila(self, paciente: Paciente) -> tuple:
        return (
            paciente.nombre or "",
            paciente.obra_social or "",
            paciente.numero_afiliado or "",
            paciente.telefono or "",
        )

    def obtener_id(self, paciente: Paciente) -> int:
        return paciente.id
