"""
ui_helpers.py — Correct SnackBar and Dialog helpers for Flet 0.86.3

In Flet 0.86.3:
- page.show_snack_bar() does NOT exist
- page.dialog attribute does NOT exist
- page.show_dialog() / page.pop_dialog() ARE the correct dialog APIs
- SnackBars must be added to page.overlay, then opened via .open = True
"""

import flet as ft


# Reuse a single snackbar per page to avoid overlay accumulation
_snackbars = {}

def show_snackbar(page, snackbar):
    """
    Show a SnackBar on the page (Flet 0.86.3 compatible).
    Reuses a single snackbar per page — replaces old one in overlay.
    """
    page_id = id(page)
    if page_id in _snackbars:
        old = _snackbars[page_id]
        if old in page.overlay:
            idx = page.overlay.index(old)
            page.overlay[idx] = snackbar
        else:
            page.overlay.append(snackbar)
    else:
        page.overlay.append(snackbar)
    _snackbars[page_id] = snackbar
    snackbar.open = True
    page.update()





def show_dialog(page, dialog):
    """
    Show a dialog on the page (Flet 0.86.3 compatible).
    Uses page.show_dialog() which is the correct API.
    """
    page.show_dialog(dialog)
    page.update()


def close_dialog(page):
    """
    Close the currently open dialog (Flet 0.86.3 compatible).
    Uses page.pop_dialog() which is the correct API.
    """
    page.pop_dialog()
    page.update()


def make_snackbar(text, bgcolor=None, duration=3000, **kwargs):
    """Create a SnackBar with the given text and optional styling."""
    content = ft.Text(text) if isinstance(text, str) else text
    params = {"content": content, "duration": duration}
    if bgcolor:
        params["bgcolor"] = bgcolor
    params.update(kwargs)
    return ft.SnackBar(**params)


def show_snack(page, text, bgcolor=None, duration=3000, **kwargs):
    """Shorthand: create + show a SnackBar in one call."""
    sb = make_snackbar(text, bgcolor=bgcolor, duration=duration, **kwargs)
    show_snackbar(page, sb)
    return sb


# ============================================================================
# FILE DIALOGS (tkinter fallback — Flet 0.86.3 FilePicker is broken)
# ============================================================================

def pick_file(title="Select file", filetypes=None):
    """Open a native file open dialog using tkinter.
    Returns the selected file path, or empty string if cancelled."""
    import tkinter as tk
    from tkinter import filedialog
    if filetypes is None:
        filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    finally:
        root.destroy()
    return path or ""


def save_file(title="Save file", default_name="", filetypes=None):
    """Open a native file save dialog using tkinter.
    Returns the selected save path, or empty string if cancelled."""
    import tkinter as tk
    from tkinter import filedialog
    if filetypes is None:
        filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        path = filedialog.asksaveasfilename(
            title=title, defaultextension=".xlsx",
            initialfile=default_name, filetypes=filetypes
        )
    finally:
        root.destroy()
    return path or ""



