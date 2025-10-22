# ui_theme.py
import tkinter as tk
from tkinter import ttk

PALETTE = {
    "bg":        "#F7F7FB",
    "fg":        "#1F2937",
    "muted":     "#6B7280",
    "primary":   "#2563EB",
    "primary-2": "#1D4ED8",
    "border":    "#E5E7EB",
    "surface":   "#FFFFFF",
    "row-alt":   "#F3F4F6",
    "focus":     "#93C5FD"
}

def apply_minimal_style(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use('clam')

    # Base
    root.configure(background=PALETTE["bg"])
    style.configure(".", background=PALETTE["bg"], foreground=PALETTE["fg"], font=("Segoe UI", 10))

    # Frames y LabelFrames como "cards"
    style.configure("Card.TFrame", background=PALETTE["surface"], relief="flat")
    style.configure("Card.TLabelframe", background=PALETTE["surface"])
    style.configure("Card.TLabelframe.Label", background=PALETTE["surface"], foreground=PALETTE["muted"], font=("Segoe UI Semibold", 10))

    # Labels / Entries
    style.configure("TLabel", background=PALETTE["surface"], foreground=PALETTE["fg"])
    style.configure("TEntry", fieldbackground="#FFFFFF", bordercolor=PALETTE["border"], lightcolor=PALETTE["focus"], darkcolor=PALETTE["border"])
    style.map("TEntry", bordercolor=[("focus", PALETTE["primary"])], lightcolor=[("focus", PALETTE["focus"])])

    # Botones
    style.configure("Accent.TButton",
                    padding=8,
                    background=PALETTE["primary"],
                    foreground="#FFFFFF",
                    borderwidth=0)
    style.map("Accent.TButton", background=[("active", PALETTE["primary-2"])])
    style.configure("Ghost.TButton",
                    padding=8,
                    background=PALETTE["surface"],
                    foreground=PALETTE["fg"],
                    borderwidth=1,
                    relief="solid",
                    bordercolor=PALETTE["border"])
    style.map("Ghost.TButton", bordercolor=[("focus", PALETTE["primary"])], foreground=[("disabled", PALETTE["muted"])])

    # Treeview
    style.configure("Minimal.Treeview",
                    background="#FFFFFF",
                    foreground=PALETTE["fg"],
                    fieldbackground="#FFFFFF",
                    rowheight=26,
                    bordercolor=PALETTE["border"],
                    lightcolor=PALETTE["border"],
                    darkcolor=PALETTE["border"])
    style.configure("Minimal.Treeview.Heading",
                    background=PALETTE["surface"],
                    foreground=PALETTE["muted"],
                    relief="flat",
                    font=("Segoe UI Semibold", 9))
    style.map("Minimal.Treeview.Heading", background=[("active", PALETTE["surface"])])
