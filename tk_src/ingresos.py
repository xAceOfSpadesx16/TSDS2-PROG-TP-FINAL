# ingresos.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, List

from dao.managers import PacienteManager, MedicoManager, CamaManager, MovimientoManager
from tk_src import dateformat

class IngresosFrame(ttk.Frame):
    """
    Ingresos:
    - Formulario: Paciente, Médico, Cama libre, Fecha de ingreso (default: ahora)
    - Acciones: Registrar / Limpiar / (Refrescar)
    - Listado: internaciones abiertas
    UX: sin popups al cargar; si no hay camas libres, se deshabilita Registrar y se muestra un hint inline.
    """
    def __init__(self, master=None):
        super().__init__(master, padding=12, style="Card.TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Mapeos label -> id para combos
        self.map_pac: Dict[str, int] = {}
        self.map_med: Dict[str, int] = {}
        self.map_cama: Dict[str, int] = {}

        # ------- Formulario -------
        frm = ttk.Labelframe(self, text="Nuevo Ingreso", padding=12, style="Card.TLabelframe")
        frm.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 8))
        for i in (1, 3):
            frm.columnconfigure(i, weight=1)

        ttk.Label(frm, text="Paciente").grid(row=0, column=0, sticky="w", padx=(6, 8), pady=4)
        self.cmb_pac = ttk.Combobox(frm, state="readonly")
        self.cmb_pac.grid(row=0, column=1, sticky="ew", padx=(0, 6), pady=4)

        ttk.Label(frm, text="Médico").grid(row=0, column=2, sticky="w", padx=(6, 8), pady=4)
        self.cmb_med = ttk.Combobox(frm, state="readonly")
        self.cmb_med.grid(row=0, column=3, sticky="ew", padx=(0, 6), pady=4)

        ttk.Label(frm, text="Cama libre").grid(row=1, column=0, sticky="w", padx=(6, 8), pady=4)
        self.cmb_cama = ttk.Combobox(frm, state="readonly")
        self.cmb_cama.grid(row=1, column=1, sticky="ew", padx=(0, 6), pady=4)

        ttk.Label(frm, text="Fecha ingreso").grid(row=1, column=2, sticky="w", padx=(6, 8), pady=4)
        self.ent_fecha = ttk.Entry(frm)
        self.ent_fecha.grid(row=1, column=3, sticky="ew", padx=(0, 6), pady=4)
        self.ent_fecha.insert(0, dateformat.now_ui_string())

        # Hint inline si no hay camas (sin popup)
        self.lbl_camas_hint = ttk.Label(frm, text="No hay camas libres.", foreground="#6B7280")
        self.lbl_camas_hint.grid(row=2, column=1, sticky="w", padx=(0, 6), pady=(0, 4))
        self.lbl_camas_hint.grid_remove()

        # Botones
        self.btn_reg = ttk.Button(frm, text="Registrar", style="Accent.TButton", command=self._registrar)
        btn_clr      = ttk.Button(frm, text="Limpiar",   style="Ghost.TButton",  command=self._limpiar)
        btn_ref      = ttk.Button(frm, text="Refrescar", style="Ghost.TButton",  command=self.refrescar)

        # Movemos botones a fila 3 para dejar el hint en fila 2
        btn_clr.grid(row=3, column=2, sticky="e", padx=(0, 6), pady=(8, 0))
        self.btn_reg.grid(row=3, column=3, sticky="e", padx=(0, 6), pady=(8, 0))
        btn_ref.grid(row=3, column=1, sticky="w", padx=(0, 6), pady=(8, 0))

        # ------- Listado -------
        cols = ("paciente", "medico", "habitacion", "cama", "fecha", "mid")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", style="Minimal.Treeview")
        self.tree.heading("paciente",   text="Paciente",    anchor="w")
        self.tree.heading("medico",     text="Médico",      anchor="w")
        self.tree.heading("habitacion", text="Habitación",  anchor="center")
        self.tree.heading("cama",       text="Cama",        anchor="center")
        self.tree.heading("fecha",      text="Ingreso",     anchor="center")
        self.tree.heading("mid",        text="ID Mov.",     anchor="center")
        self.tree.column("paciente",   width=240, anchor="w")
        self.tree.column("medico",     width=200, anchor="w")
        self.tree.column("habitacion", width=120, anchor="center")
        self.tree.column("cama",       width=80,  anchor="center")
        self.tree.column("fecha",      width=160, anchor="center")
        self.tree.column("mid",        width=90,  anchor="center")
        vs = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vs.set)
        self.tree.tag_configure("alt", background="#F3F4F6")
        self.tree.grid(row=1, column=0, sticky="nsew")
        vs.grid(row=1, column=1, sticky="ns")

        self._cargar_combos()
        self._cargar_internaciones()
        self._actualizar_estado_registrar()

    # ----------------- API pública -----------------
    def refrescar(self) -> None:
        """Recarga combos y grilla al volver a la pestaña."""
        self._cargar_combos()
        self._cargar_internaciones()
        self._actualizar_estado_registrar()

    # ----------------- Helpers UI -----------------
    def _show_error(self, e: Exception) -> None:
        msg = str(e).strip() or e.__class__.__name__
        messagebox.showerror("Error", msg)

    def _cargar_combos(self) -> None:
        # Pacientes
        self.map_pac.clear()
        pacs = PacienteManager.get_list()
        pac_opts: List[str] = []
        for p in pacs:
            label = f"{p.id} – {p.nombre or ''}"
            self.map_pac[label] = p.id
            pac_opts.append(label)
        self.cmb_pac["values"] = pac_opts
        if pac_opts:
            self.cmb_pac.current(0)
            self.cmb_pac.configure(state="readonly")
        else:
            self.cmb_pac.set("")
            self.cmb_pac.configure(state="disabled")

        # Médicos
        self.map_med.clear()
        meds = MedicoManager.get_list()
        med_opts: List[str] = []
        for m in meds:
            label = f"{m.id} – {m.nombre or ''} (Mat {m.matricula if m.matricula is not None else '-'})"
            self.map_med[label] = m.id
            med_opts.append(label)
        self.cmb_med["values"] = med_opts
        if med_opts:
            self.cmb_med.current(0)
            self.cmb_med.configure(state="readonly")
        else:
            self.cmb_med.set("")
            self.cmb_med.configure(state="disabled")

        # Camas libres
        self._recargar_camas_libres()

    def _recargar_camas_libres(self) -> None:
        self.map_cama.clear()
        libres = CamaManager.camas_libres()
        cama_opts: List[str] = []
        for c in libres:
            label = f"Cama {c.id} (Hab {c.habitacion_id})"
            self.map_cama[label] = c.id
            cama_opts.append(label)

        self.cmb_cama["values"] = cama_opts
        if cama_opts:
            self.cmb_cama.current(0)
            self.cmb_cama.configure(state="readonly")
            self.lbl_camas_hint.grid_remove()
        else:
            # Sin popup: solo deshabilitamos y mostramos hint inline
            self.cmb_cama.set("")
            self.cmb_cama.configure(state="disabled")
            self.lbl_camas_hint.grid()

        self._actualizar_estado_registrar()

    def _actualizar_estado_registrar(self) -> None:
        # Habilitar Registrar solo si hay opciones válidas en los tres combos
        hay_pac = bool(self.cmb_pac["values"])
        hay_med = bool(self.cmb_med["values"])
        hay_cama = bool(self.cmb_cama["values"])
        if hay_pac and hay_med and hay_cama:
            self.btn_reg.state(["!disabled"])
        else:
            self.btn_reg.state(["disabled"])

    def _cargar_internaciones(self) -> None:
        self.tree.delete(*self.tree.get_children())
        filas = MovimientoManager.detalle_camas_ocupadas()
        for i, d in enumerate(filas):
            paciente = d.get("paciente", "-") if isinstance(d, dict) else d[1]
            medico   = d.get("medico", "-") if isinstance(d, dict) else "-"
            habitac  = d.get("habitacion_numero", "-") if isinstance(d, dict) else d[3]
            cama_id  = d.get("cama_id", "-") if isinstance(d, dict) else d[2]
            fecha    = d.get("fecha_ingreso", "-") if isinstance(d, dict) else "-"
            # >>> formatear a UI si viene datetime/iso <<<
            fecha_ui = dateformat.to_ui_datetime(fecha) if fecha != "-" else "-"
            mov_id   = d.get("movimiento_id", "-") if isinstance(d, dict) else d[0]
            tags = ("alt",) if i % 2 else ()
            self.tree.insert("", "end", values=(paciente, medico, habitac, cama_id, fecha_ui, mov_id), tags=tags)

    # ----------------- Acciones -----------------
    def _registrar(self) -> None:
        # Validación de combos
        if not self.cmb_pac.get() or not self.cmb_med.get():
            self._show_error(ValueError("Completá Paciente y Médico."))
            return
        if not self.cmb_cama.get():
            # Recién aquí mostramos un error si el usuario intenta registrar sin camas
            self._show_error(ValueError("No hay camas libres."))
            return

        paciente_id = self.map_pac[self.cmb_pac.get()]
        medico_id   = self.map_med[self.cmb_med.get()]
        cama_id     = self.map_cama[self.cmb_cama.get()]

        # Fecha
        raw = self.ent_fecha.get().strip()
        try:
            fecha = dateformat.parse_ui_datetime_strict(raw)
        except ValueError:
            try:
                fecha = datetime.fromisoformat(raw)
            except Exception:
                self._show_error(ValueError("Formato inválido. Use dd/mm/YYYY HH:MM"))
                return

        # Persistencia
        try:
            MovimientoManager.ingresar(
                cama_id=cama_id, paciente_id=paciente_id, medico_id=medico_id, fecha_ingreso=fecha
            )
            messagebox.showinfo("OK", "Ingreso registrado.")
            # refrescos
            self._recargar_camas_libres()
            self._cargar_internaciones()
        except Exception as e:
            self._show_error(e)

    def _limpiar(self) -> None:
        if self.cmb_pac["values"]:
            self.cmb_pac.current(0)
        if self.cmb_med["values"]:
            self.cmb_med.current(0)
        if self.cmb_cama["values"]:
            self.cmb_cama.current(0)

        self.ent_fecha.delete(0, "end")
        # ANTES: datetime.now().replace(...).isoformat(" ")
        self.ent_fecha.insert(0, dateformat.now_ui_string())

        self._actualizar_estado_registrar()