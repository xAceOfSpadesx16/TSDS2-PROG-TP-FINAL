# altas.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, Dict, Any

from dao.managers import MovimientoManager
from tk_src import dateformat


class AltasFrame(ttk.Frame):
    """
    Altas de internaciones:
    - Listado de internaciones abiertas (movimientos con fecha_egreso NULL)
    - Selección de una fila -> carga form (solo lectura excepto 'Fecha de alta')
    - Botones: Dar alta / Limpiar / Refrescar
    - Usa los Managers/Models para todo (dar_alta valida fecha >= ingreso)
    """
    def __init__(self, master=None):
        super().__init__(master, padding=12, style="Card.TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Estado seleccionado
        self._selected_mov_id: Optional[int] = None

        # -------- Formulario (solo lectura excepto 'Fecha de alta') --------
        frm = ttk.Labelframe(self, text="Alta de Internación", padding=12, style="Card.TLabelframe")
        frm.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 8))
        for col in (1, 3):
            frm.columnconfigure(col, weight=1)

        # Paciente / Médico
        ttk.Label(frm, text="Paciente").grid(row=0, column=0, sticky="w", padx=(6,8), pady=4)
        self.ent_paciente = ttk.Entry(frm, state="disabled")
        self.ent_paciente.grid(row=0, column=1, sticky="ew", padx=(0,6), pady=4)

        ttk.Label(frm, text="Médico").grid(row=0, column=2, sticky="w", padx=(6,8), pady=4)
        self.ent_medico = ttk.Entry(frm, state="disabled")
        self.ent_medico.grid(row=0, column=3, sticky="ew", padx=(0,6), pady=4)

        # Habitación / Cama
        ttk.Label(frm, text="Habitación").grid(row=1, column=0, sticky="w", padx=(6,8), pady=4)
        self.ent_habitacion = ttk.Entry(frm, state="disabled", width=20)
        self.ent_habitacion.grid(row=1, column=1, sticky="ew", padx=(0,6), pady=4)

        ttk.Label(frm, text="Cama").grid(row=1, column=2, sticky="w", padx=(6,8), pady=4)
        self.ent_cama = ttk.Entry(frm, state="disabled", width=20)
        self.ent_cama.grid(row=1, column=3, sticky="ew", padx=(0,6), pady=4)

        # Fechas
        ttk.Label(frm, text="Ingreso").grid(row=2, column=0, sticky="w", padx=(6,8), pady=4)
        self.ent_ingreso = ttk.Entry(frm, state="disabled")
        self.ent_ingreso.grid(row=2, column=1, sticky="ew", padx=(0,6), pady=4)

        ttk.Label(frm, text="Fecha de alta").grid(row=2, column=2, sticky="w", padx=(6,8), pady=4)
        self.ent_alta = ttk.Entry(frm)
        self.ent_alta.grid(row=2, column=3, sticky="ew", padx=(0,6), pady=4)
        self._set_fecha_alta_default()

        # Botones
        self.btn_alta = ttk.Button(frm, text="Dar alta", style="Accent.TButton", command=self._dar_alta)
        btn_clr      = ttk.Button(frm, text="Limpiar",  style="Ghost.TButton",  command=self._limpiar)
        btn_ref      = ttk.Button(frm, text="Refrescar",style="Ghost.TButton",  command=self.refrescar)

        btn_ref.grid( row=3, column=1, sticky="w", padx=(0,6), pady=(8,0))
        btn_clr.grid( row=3, column=2, sticky="e", padx=(0,6), pady=(8,0))
        self.btn_alta.grid(row=3, column=3, sticky="e", padx=(0,6), pady=(8,0))

        # -------- Listado internaciones abiertas --------
        cols = ("paciente","medico","habitacion","cama","ingreso","mid")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", style="Minimal.Treeview")
        for cid, title, width, anchor in (
            ("paciente","Paciente",240,"w"),
            ("medico","Médico",200,"w"),
            ("habitacion","Habitación",120,"center"),
            ("cama","Cama",80,"center"),
            ("ingreso","Ingreso",160,"center"),
            ("mid","ID Mov.",90,"center"),
        ):
            self.tree.heading(cid, text=title, anchor=anchor)
            self.tree.column(cid, width=width, anchor=anchor, stretch=(cid in ("paciente","medico")))
        vs = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vs.set)
        self.tree.tag_configure("alt", background="#F3F4F6")
        self.tree.grid(row=1, column=0, sticky="nsew")
        vs.grid(row=1, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Carga inicial
        self._cargar_abiertas()
        self._update_btn_state()

    # ---------- API pública para refrescar desde el Notebook ----------
    def refrescar(self) -> None:
        self._cargar_abiertas()
        self._update_btn_state()

    # ---------- Helpers ----------
    def _show_error(self, e: Exception) -> None:
        messagebox.showerror("Error", (str(e).strip() or e.__class__.__name__))

    def _set_fecha_alta_default(self) -> None:
        self.ent_alta.delete(0, "end")
        self.ent_alta.insert(0, dateformat.now_ui_string())

    def _clear_form(self) -> None:
        for w in (self.ent_paciente, self.ent_medico, self.ent_habitacion, self.ent_cama, self.ent_ingreso):
            w.configure(state="normal"); w.delete(0, "end"); w.configure(state="disabled")
        self._set_fecha_alta_default()

    def _load_form(self, detalle: Dict[str, Any]) -> None:
        self._clear_form()
        self.ent_paciente.configure(state="normal"); self.ent_paciente.insert(0, detalle.get("paciente","-")); self.ent_paciente.configure(state="disabled")
        self.ent_medico.configure(state="normal");   self.ent_medico.insert(0, detalle.get("medico","-"));     self.ent_medico.configure(state="disabled")
        self.ent_habitacion.configure(state="normal"); self.ent_habitacion.insert(0, str(detalle.get("habitacion_numero","-"))); self.ent_habitacion.configure(state="disabled")
        self.ent_cama.configure(state="normal");       self.ent_cama.insert(0, str(detalle.get("cama_id","-")));                 self.ent_cama.configure(state="disabled")

        ingreso_val = detalle.get("fecha_ingreso", "-")
        self.ent_ingreso.configure(state="normal")
        self.ent_ingreso.insert(0, ingreso_val)
        self.ent_ingreso.configure(state="disabled")

    def _cargar_abiertas(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self._selected_mov_id = None

        filas = MovimientoManager.detalle_camas_ocupadas()
        for i, d in enumerate(filas):
            tags = ("alt",) if i % 2 else ()
            fecha_ui = dateformat.to_ui_datetime(d.get("fecha_ingreso")) if d.get("fecha_ingreso") else "-"
            self.tree.insert(
                "", "end",
                iid=str(d["movimiento_id"]),
                values=(
                    d.get("paciente","-"),
                    d.get("medico","-"),
                    d.get("habitacion_numero","-"),
                    d.get("cama_id","-"),
                    fecha_ui,
                    d.get("movimiento_id","-"),
                ),
                tags=tags
            )

        if not filas:
            self._clear_form()

    def _update_btn_state(self) -> None:
        if self._selected_mov_id is None:
            self.btn_alta.state(["disabled"])
        else:
            self.btn_alta.state(["!disabled"])

    # ---------- Eventos ----------
    def _on_select(self, _evt=None) -> None:
        sel = self.tree.selection()
        if not sel:
            self._selected_mov_id = None
            self._clear_form()
            self._update_btn_state()
            return
        self._selected_mov_id = int(sel[0])
        # Para el form, aprovechamos el dict del listado:
        item = self.tree.item(sel[0])
        vals = item["values"]
        detalle = {
            "paciente": vals[0],
            "medico": vals[1],
            "habitacion_numero": vals[2],
            "cama_id": vals[3],
            "fecha_ingreso": vals[4],
            "movimiento_id": vals[5],
        }
        self._load_form(detalle)
        self._set_fecha_alta_default()
        self._update_btn_state()

    def _limpiar(self) -> None:
        """Deselecciona la fila actual y limpia el formulario."""
        self._selected_mov_id = None
        try:
            self.tree.selection_remove(self.tree.selection())
        except Exception:
            pass
        self._clear_form()
        self._set_fecha_alta_default()
        self._update_btn_state()


    # ---------- Acción principal ----------
    def _dar_alta(self) -> None:
        if self._selected_mov_id is None:
            self._show_error(ValueError("Seleccioná una internación."))
            return

        # Parseo de fecha alta
        raw = self.ent_alta.get().strip()
        try:
            fecha_alta = dateformat.parse_ui_datetime_strict(raw)
        except ValueError:
            self._show_error(ValueError("Formato inválido. Use dd/mm/YYYY HH:MM"))
            return

        try:
            # Delega validación (>= ingreso, no doble alta) al Manager
            MovimientoManager.dar_alta(self._selected_mov_id, fecha_alta)
            messagebox.showinfo("OK", "Alta registrada.")
            # Refrescos
            self._selected_mov_id = None
            self._cargar_abiertas()
            self._update_btn_state()
        except Exception as e:
            self._show_error(e)

    # ---------- Integración: llamada externa desde Notebook ----------
    def refrescar(self) -> None:
        self._cargar_abiertas()
        self._update_btn_state()
