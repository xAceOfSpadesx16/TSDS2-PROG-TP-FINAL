# table_view.py
import tkinter as tk
from tkinter import ttk
from typing import Callable, Iterable, Sequence, Optional, Any

class SimpleTable(ttk.Frame):
    """
    Treeview reutilizable.
    - columns: lista de dicts con: id, title, width (opcional), stretch (bool, opcional), anchor (opcional)
    - on_select(iid: str) -> None callback al seleccionar
    - set_rows(rows, iid_getter): carga filas, usando iid= iid_getter(row)
    - sort habilitado click en header
    """
    def __init__(self, master, columns: Sequence[dict], on_select: Optional[Callable[[str], None]] = None):
        super().__init__(master)
        self.on_select = on_select
        self.columns = columns
        self._sort_state: dict[str, bool] = {}  # col_id -> asc(True)/desc(False)

        self.tree = ttk.Treeview(self, columns=[c["id"] for c in columns], show="headings", style="Minimal.Treeview")
        vs = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vs.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        for col in columns:
            cid = col["id"]
            self.tree.heading(cid, text=col.get("title", cid), command=lambda c=cid: self._on_heading_click(c), anchor=col.get("anchor", "w"))
            self.tree.column(
                cid,
                width=col.get("width", 120),
                stretch=bool(col.get("stretch", True)),
                anchor=col.get("anchor", "w")
            )

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Zebra striping
        self.tree.tag_configure("alt", background="#F3F4F6")

    def clear(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)

    def set_rows(self, rows: Iterable[Any], iid_getter: Callable[[Any], str], values_getter: Callable[[Any], Sequence[Any]]):
        self.clear()
        for idx, row in enumerate(rows):
            iid = str(iid_getter(row))
            vals = list(values_getter(row))
            tags = ("alt",) if idx % 2 else ()
            self.tree.insert("", "end", iid=iid, values=vals, tags=tags)

    def get_selected_iid(self) -> Optional[str]:
        sel = self.tree.selection()
        return sel[0] if sel else None

    def focus_iid(self, iid: str):
        if not iid: return
        try:
            self.tree.see(iid)
            self.tree.selection_set(iid)
            self.tree.focus(iid)
        except tk.TclError:
            pass

    # -------- interno --------
    def _on_select(self, _evt=None):
        if self.on_select:
            iid = self.get_selected_iid()
            if iid:
                self.on_select(iid)

    def _on_heading_click(self, col_id: str):
        """
        Ordena por la columna col_id alternando asc/desc.
        """
        data = [(self.tree.set(k, col_id), k) for k in self.tree.get_children("")]
        # detectar si datos son numéricos
        def try_num(x):
            try:
                return float(x)
            except (TypeError, ValueError):
                return x

        data = [(try_num(v), k) for v, k in data]
        asc = not self._sort_state.get(col_id, True)
        data.sort(reverse=not asc)
        for idx, (_v, k) in enumerate(data):
            self.tree.move(k, "", idx)
            self.tree.item(k, tags=("alt",) if idx % 2 else ())
        self._sort_state[col_id] = asc
