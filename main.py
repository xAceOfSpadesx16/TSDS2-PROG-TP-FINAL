import tkinter as tk
from tkinter import ttk

from dao.managers import (
    BaseManager,
    PacienteManager,
    MedicoManager,
    HabitacionManager,
    MovimientoManager,
    CamaManager
)

from tk_src import ABMMedicosFrame, ABMPacientesFrame, IngresosFrame, ABMHabitacionesFrame, ABMCamasFrame, AltasFrame, InformesFrame
from tk_src.ui_theme import apply_minimal_style

def inicializar_tablas() -> None:
    managers: list[BaseManager] = [
        PacienteManager,
        MedicoManager,
        HabitacionManager,
        MovimientoManager,
        CamaManager
    ]
    for manager in managers:
        print(f"Inicializando tabla para {manager.model.__name__}...")
        manager.create_table()
    print("Tablas inicializadas.")

def main() -> None:
    # Inicialización de esquema
    inicializar_tablas()

    def _on_tab_changed(evt):
        nb = evt.widget  # ttk.Notebook
        tab_id = nb.select()
        widget = nb.nametowidget(tab_id)
        if hasattr(widget, "refrescar"):
            widget.refrescar()


    # UI
    root = tk.Tk()
    root.title("Nosocomio - Administración")

    apply_minimal_style(root)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    notebook.bind("<<NotebookTabChanged>>", _on_tab_changed)

    tab_ingresos = IngresosFrame(notebook)
    notebook.add(tab_ingresos, text="Ingresos")
    
    tab_altas = AltasFrame(notebook)
    notebook.add(tab_altas, text="Altas")

    tab_medicos = ABMMedicosFrame(notebook, titulo="Médico")
    notebook.add(tab_medicos, text="Médicos")

    tab_pacientes = ABMPacientesFrame(notebook, titulo="Paciente")
    notebook.add(tab_pacientes, text="Pacientes")

    tab_habs = ABMHabitacionesFrame(notebook, titulo="Habitación")
    notebook.add(tab_habs, text="Habitaciones")

    tab_camas = ABMCamasFrame(notebook, titulo="Cama")
    notebook.add(tab_camas, text="Camas")

    tab_informes = InformesFrame(notebook)
    notebook.add(tab_informes, text="Informes")

    root.minsize(720, 520)
    root.mainloop()


if __name__ == "__main__":
    main()