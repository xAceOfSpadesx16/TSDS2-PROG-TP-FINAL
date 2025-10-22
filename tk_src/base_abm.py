import tkinter as tk
import sqlite3
from tkinter import ttk, messagebox
from typing import Any, Sequence
from tk_src.table_view import SimpleTable

class BaseABMFrame(ttk.Frame):
    """
    Base ABM reutilizable con:
    - Formulario (arriba)
    - Listado (Treeview) abajo
    - Botonera: Nuevo / Modificar / Eliminar / Guardar / Cancelar
    Reglas:
    - El campo 'id' no se muestra en creación y se muestra (disabled) en edición.
    Subclases deben implementar:
    - manager (propiedad con CRUD)
    - definir_campos_form()
    - setear_desde_modelo(instancia|None)
    - recolectar_para_guardar() -> dict
    - columnas_listado() -> list[dict]
    - mapear_modelo_a_fila(instancia) -> Sequence
    - obtener_id(instancia) -> Any
    """
    def __init__(self, master=None, titulo: str = "Formulario"):
        super().__init__(master, padding=12, style="Card.TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Estado
        self.registros: list[Any] = []
        self.indice_actual: int = -1
        self.estado: str = "lectura"        # 'lectura' | 'edicion'
        self.modo_creacion: bool = False

        # Formulario (LabelFrame tipo card)
        self.frm_form = ttk.Labelframe(self, text=titulo, style="Card.TLabelframe", padding=12)
        self.frm_form.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 8))
        self.frm_form.columnconfigure(1, weight=1)

        # Controles formulario (definidos por subclase)
        self.variables_por_campo: dict[str, tk.Variable] = {}
        self.inputs_por_campo: dict[str, ttk.Entry] = {}
        self.labels_por_campo: dict[str, ttk.Label] = {}

        self.definir_campos_form()

        # Botonera
        self._construir_botonera()

        # Listado reutilizable
        self.tabla = SimpleTable(self, self.columnas_listado(), on_select=self._on_row_select)
        self.tabla.grid(row=2, column=0, sticky="nsew", padx=2, pady=(0, 4))

        # Carga inicial
        self.refrescar_lista()
        self._refrescar_estado_ui()

    # --------- API esperada en subclase ----------
    @property
    def manager(self):
        raise NotImplementedError

    def _mostrar_error(self, error: Exception) -> None:
        mensaje = str(error).strip() or error.__class__.__name__
        messagebox.showerror("Error", mensaje)

    def definir_campos_form(self) -> None:
        raise NotImplementedError

    def setear_desde_modelo(self, instancia: Any | None) -> None:
        raise NotImplementedError

    def recolectar_para_guardar(self) -> dict:
        raise NotImplementedError

    def columnas_listado(self) -> Sequence[dict]:
        raise NotImplementedError

    def mapear_modelo_a_fila(self, instancia: Any) -> Sequence[Any]:
        raise NotImplementedError

    def obtener_id(self, instancia: Any) -> Any:
        return getattr(instancia, "id", None)

    # --------- Infraestructura común ----------
    def _construir_botonera(self):
        bar = ttk.Frame(self, style="Card.TFrame")
        bar.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        for i in range(10):
            bar.columnconfigure(i, weight=1)

        self.btn_nuevo    = ttk.Button(bar, text="Nuevo",     style="Accent.TButton", command=self.on_nuevo)
        self.btn_modif    = ttk.Button(bar, text="Modificar", style="Ghost.TButton",  command=self.on_modificar)
        self.btn_eliminar = ttk.Button(bar, text="Eliminar",  style="Ghost.TButton",  command=self.on_eliminar)
        self.btn_guardar  = ttk.Button(bar, text="Guardar",   style="Accent.TButton", command=self.on_guardar)
        self.btn_cancelar = ttk.Button(bar, text="Cancelar",  style="Ghost.TButton",  command=self.on_cancelar)

        self.btn_nuevo.grid(   row=0, column=6, padx=4)
        self.btn_modif.grid(   row=0, column=7, padx=4)
        self.btn_eliminar.grid(row=0, column=8, padx=4)
        self.btn_guardar.grid( row=0, column=9, padx=4)
        self.btn_cancelar.grid(row=0, column=10, padx=4)

    def refrescar_lista(self):
        self.registros = self.manager.get_list()
        # Cargar tabla
        self.tabla.set_rows(
            self.registros,
            iid_getter=lambda x: self.obtener_id(x),
            values_getter=lambda x: self.mapear_modelo_a_fila(x)
        )
        # Selección actual
        if self.registros:
            if 0 <= self.indice_actual < len(self.registros):
                iid = str(self.obtener_id(self.registros[self.indice_actual]))
                self.tabla.focus_iid(iid)
                self.setear_desde_modelo(self.registros[self.indice_actual])
            else:
                self.indice_actual = 0
                iid = str(self.obtener_id(self.registros[0]))
                self.tabla.focus_iid(iid)
                self.setear_desde_modelo(self.registros[0])
        else:
            self.indice_actual = -1
            self.setear_desde_modelo(None)

        self._refrescar_estado_ui()

    def _habilitar_formulario(self, habilitar: bool):
        for nombre, widget in self.inputs_por_campo.items():
            if nombre == "id":
                # id siempre deshabilitado (solo lectura)
                if isinstance(widget, ttk.Combobox):
                    widget.configure(state="disabled")
                else:
                    widget.state(["disabled"])
                continue

            # Soporte para Combobox: 'readonly' en edición, 'disabled' en lectura
            if isinstance(widget, ttk.Combobox):
                widget.configure(state="readonly" if habilitar else "disabled")
            else:
                widget.state(["!disabled"] if habilitar else ["disabled"])

    def _mostrar_id(self, visible: bool):
        lbl = self.labels_por_campo.get("id")
        ent = self.inputs_por_campo.get("id")
        if not lbl or not ent:
            return
        if visible:
            lbl.grid()
            ent.grid()
        else:
            lbl.grid_remove()
            ent.grid_remove()

    def _refrescar_estado_ui(self):
        en_lectura = (self.estado == "lectura")
        hay = len(self.registros) > 0

        self._habilitar_formulario(not en_lectura)
        self._mostrar_id(visible=(not self.modo_creacion and en_lectura) or (not self.modo_creacion and not en_lectura))

        # Habilitar/Deshabilitar tabla
        self.tabla.tree.configure(selectmode="browse" if en_lectura else "none")

        # Acciones
        self.btn_nuevo.state(["!disabled"] if en_lectura else ["disabled"])
        self.btn_modif.state(["!disabled"] if en_lectura and hay else ["disabled"])
        self.btn_eliminar.state(["!disabled"] if en_lectura and hay else ["disabled"])
        self.btn_guardar.state(["!disabled"] if not en_lectura else ["disabled"])
        self.btn_cancelar.state(["!disabled"] if not en_lectura else ["disabled"])

    def refrescar(self) -> None:
        """Permite que la pestaña se refresque externamente (p.ej., al cambiar de tab)."""
        self.refrescar_lista()

    # -------- Selección en tabla --------
    def _on_row_select(self, iid: str):
        if self.estado != "lectura":
            return
        # buscar índice por iid
        for idx, reg in enumerate(self.registros):
            if str(self.obtener_id(reg)) == iid:
                self.indice_actual = idx
                self.setear_desde_modelo(reg)
                break

    # -------- Acciones --------
    def on_nuevo(self):
        self.estado = "edicion"
        self.modo_creacion = True
        self.setear_desde_modelo(None)
        self._mostrar_id(False)
        self._refrescar_estado_ui()

    def on_modificar(self):
        if self.indice_actual < 0: return
        self.estado = "edicion"
        self.modo_creacion = False
        self._mostrar_id(True)
        self._refrescar_estado_ui()

    def on_eliminar(self):
        if self.indice_actual < 0:
            return
        actual = self.registros[self.indice_actual]
        if not messagebox.askyesno("Confirmar", "¿Eliminar el registro seleccionado?"):
            return
        try:
            self.manager.delete(actual.id)
            self.indice_actual = max(0, self.indice_actual - 1)
            self.refrescar_lista()
            messagebox.showinfo("OK", "Registro eliminado.")
        except Exception as err:
            self._mostrar_error(err)

    def on_guardar(self):
        # 1) Validaciones de formulario.
        try:
            datos = self.recolectar_para_guardar()
        except Exception as err:
            self._mostrar_error(err)
            return

        # 2) Persistencia (create/update) con manejo unificado
        try:
            if self.modo_creacion:
                creado = self.manager.create(datos)
                created_id = getattr(creado, "id", None)
                messagebox.showinfo("OK", f"Registro creado (id={created_id}).")
            else:
                actual = self.registros[self.indice_actual]
                actualizado = self.manager.update(actual.id, {"id": actual.id, **datos})
                created_id = getattr(actualizado, "id", None)
                messagebox.showinfo("OK", f"Registro actualizado (id={created_id}).")
        except Exception as err:
            self._mostrar_error(err)
            return

        # 3) Refresco
        self.estado = "lectura"
        self.modo_creacion = False
        self.refrescar_lista()
        if created_id is not None:
            self.tabla.focus_iid(str(created_id))

    def on_cancelar(self):
        self.estado = "lectura"
        self.modo_creacion = False
        if 0 <= self.indice_actual < len(self.registros):
            self.setear_desde_modelo(self.registros[self.indice_actual])
        else:
            self.setear_desde_modelo(None)
        self._refrescar_estado_ui()
