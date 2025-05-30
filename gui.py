import tkinter as tk
from tkinter import ttk
import analyze_gui
import scraper_gui

def center_window(window, width=720, height=400):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Wiki Scraper - Menu Chính")
        self.root.geometry("400x200")

        ttk.Label(root, text="🧠 Wiki Scraper", font=("Segoe UI", 16, "bold")).pack(pady=(30, 10))

        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="🔍 Phân tích Section ID", width=30, command=self.open_analyze).pack(pady=5)
        ttk.Button(button_frame, text="🧹 Scrape Wiki", width=30, command=self.open_scraper).pack(pady=5)

    def open_analyze(self):
        self.root.withdraw()
        analyze_gui.start_gui(self.root)

    def open_scraper(self):
        self.root.withdraw()
        scraper_gui.start_gui(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    center_window(root, 400, 200)
    MainMenu(root)
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()


