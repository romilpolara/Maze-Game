import tkinter as tk
from tkinter import font as tkFont

def list_available_fonts():
    root = tk.Tk()
    available_fonts = list(tkFont.families())
    root.destroy()
    return available_fonts

# List all available fonts
fonts = list_available_fonts()
print("Available fonts:", fonts)
