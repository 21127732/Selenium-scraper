
import tkinter as tk
from tkinter import ttk
from scraper import init_driver, list_unique_links_from_section, quit_driver
import os
import csv

def center_window(window, width=780, height=520):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def load_section_ids_from_analyze(url):
    folder = "Analyze Output"
    if not os.path.exists(folder):
        return []
    for file in os.listdir(folder):
        if file.endswith(".csv"):
            with open(os.path.join(folder, file), encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                if rows and rows[0][0] == "URL" and rows[0][1].strip() == url:
                    return [row[1] for row in rows[2:] if len(row) > 1]
    return []

def start_gui(parent_root):
    new_window = tk.Toplevel()
    center_window(new_window)
    ScraperApp(new_window, parent_root)

class ScraperSection:
    def __init__(self, master, remove_callback):
        self.frame = ttk.Frame(master)
        self.frame.pack(padx=10, pady=5, fill=tk.X)

        self.url_var = tk.StringVar()
        self.section_var = tk.StringVar()
        self.name_var = tk.StringVar()

        self.remove_button = tk.Button(self.frame, text="➖", fg="red", width=2, command=remove_callback)
        self.remove_button.grid(row=1, column=0, rowspan=3, padx=5, pady=10, sticky=tk.N)

        ttk.Label(self.frame, text="🔗 URL:").grid(row=1, column=1, sticky=tk.W)
        self.url_entry = ttk.Entry(self.frame, width=60, textvariable=self.url_var)
        self.url_entry.grid(row=1, column=2, padx=5)
        self.url_entry.insert(0, "https://limbuscompany.wiki.gg/wiki/Limbus_Company_Wiki")
        self.url_entry.bind("<FocusOut>", self.update_section_options)

        ttk.Label(self.frame, text="📁 Tên thư mục:").grid(row=2, column=1, sticky=tk.W)
        self.name_entry = ttk.Entry(self.frame, width=60, textvariable=self.name_var)
        self.name_entry.grid(row=2, column=2, padx=5)

        ttk.Label(self.frame, text="📑 Section ID:").grid(row=3, column=1, sticky=tk.W)
        self.section_combobox = ttk.Combobox(self.frame, width=57, textvariable=self.section_var)
        self.section_combobox.grid(row=3, column=2, padx=5)

    def update_section_options(self, event=None):
        url = self.url_var.get().strip()
        section_ids = load_section_ids_from_analyze(url)
        self.section_combobox['values'] = section_ids
        if section_ids:
            self.section_combobox.set(section_ids[0])

    def destroy(self):
        self.frame.destroy()

class ScraperApp:
    def __init__(self, root, parent_root=None):
        self.root = root
        self.root.title("Scraper - Wiki Scraper")
        self.parent_root = parent_root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.sections = []

        header_frame = ttk.Frame(root)
        header_frame.pack(fill=tk.X, pady=5, padx=10)

        ttk.Button(header_frame, text="← Quay lại", command=self.go_back).pack(side="left")
        self.add_button = tk.Button(header_frame, text="➕", width=3, command=self.add_section, fg="green")
        self.add_button.pack(side="right")

        self.frame = ttk.Frame(root)
        self.frame.pack()

        self.add_section()

        self.checkbox_frame = ttk.Frame(root)
        self.checkbox_frame.pack()

        self.headless_var = tk.BooleanVar(value=True)
        self.scrape_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(self.checkbox_frame, text="Chạy chế độ headless", variable=self.headless_var, command=self.on_headless_toggle).pack(anchor="w", padx=30)
        self.scrape_check = ttk.Checkbutton(self.checkbox_frame, text="Chụp ảnh từng link (scrape)", variable=self.scrape_var)
        self.scrape_check.pack(anchor="w", padx=30)

        self.run_button = ttk.Button(root, text="🚀 Bắt đầu", command=self.run_all_sections)
        self.run_button.pack(pady=10)

        self.log_text = tk.Text(root, height=10)
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.on_headless_toggle()

    def add_section(self):
        if len(self.sections) >= 3:
            return
        section = ScraperSection(self.frame, lambda s=len(self.sections): self.remove_section(s))
        self.sections.append(section)
        self.refresh_remove_buttons()
        if len(self.sections) >= 3:
            self.add_button.config(state=tk.DISABLED, fg="gray")

    def remove_section(self, index):
        if len(self.sections) <= 1:
            return
        self.sections[index].destroy()
        self.sections.pop(index)
        self.refresh_remove_buttons()
        self.add_button.config(state=tk.NORMAL, fg="green")

    def refresh_remove_buttons(self):
        for section in self.sections:
            section.remove_button.grid_forget()
        if len(self.sections) > 1:
            for section in self.sections:
                section.remove_button.grid(row=1, column=0, rowspan=3, padx=5, pady=10, sticky=tk.N)

    def on_headless_toggle(self):
        if self.headless_var.get():
            self.scrape_var.set(False)
            self.scrape_check.config(state=tk.DISABLED)
            self.log_text.insert(tk.END, "⚠️ Scrape mode tự động tắt vì đang bật chế độ Headless.")
        else:
            self.scrape_check.config(state=tk.NORMAL)

    def run_all_sections(self):
        self.log_text.delete(1.0, tk.END)
        headless = self.headless_var.get()
        scrape = self.scrape_var.get()

        for i, section in enumerate(self.sections, 1):
            url = section.url_var.get().strip()
            section_id = section.section_var.get().strip()
            name = section.name_var.get().strip()

            if not url or not section_id or not name:
                self.log_text.insert(tk.END, f"❌ Mục #{i} thiếu thông tin. Vui lòng điền đầy đủ.")
                continue

            self.log_text.insert(tk.END, f"🔍 Mục #{i}: Bắt đầu scraping {url} - #{section_id}")
            driver = init_driver(headless)
            result = list_unique_links_from_section(driver, url, section_id, name, headless, scrape)
            quit_driver(driver)

            if result == "invalid_section":
                self.log_text.insert(tk.END, f"❌ Không tìm thấy Section ID '{section_id}' trong trang.")
            elif result == "no_links":
                self.log_text.insert(tk.END, f"⚠️ Section ID '{section_id}' tồn tại nhưng không có liên kết nào.")
            elif result == "success":
                self.log_text.insert(tk.END, f"✅ Mục #{i} hoàn tất scraping!")
            else:
                self.log_text.insert(tk.END, f"❌ Đã xảy ra lỗi ở mục #{i}.")

    def go_back(self):
        self.root.destroy()
        if self.parent_root:
            self.parent_root.deiconify()

    def on_close(self):
        self.root.destroy()
        if self.parent_root:
            self.parent_root.destroy()
