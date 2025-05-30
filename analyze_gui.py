import tkinter as tk
from tkinter import ttk
from analyze import extract_section_ids
import os
import csv

def center_window(window, width=720, height=400):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def start_gui(parent_root):
    new_window = tk.Toplevel()
    center_window(new_window)
    AnalyzeApp(new_window, parent_root)

class AnalyzeApp:
    def __init__(self, root, parent_root=None):
        self.root = root
        self.parent_root = parent_root
        self.root.title("Phân tích Section ID từ URL")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Nút back
        ttk.Button(root, text="← Quay lại", command=self.go_back).pack(anchor="nw", padx=10, pady=5)

        # Khung nhập
        self.input_frame = ttk.Frame(root)
        self.input_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(self.input_frame, text="🔗 Nhập URL:").grid(row=0, column=0, sticky=tk.W, padx=10)
        self.url_entry = ttk.Entry(self.input_frame, width=70)
        self.url_entry.grid(row=0, column=1, padx=5)
        self.url_entry.insert(0, "https://limbuscompany.wiki.gg/wiki/Limbus_Company_Wiki")

        ttk.Label(self.input_frame, text="📁 Tên file lưu CSV:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.filename_entry = ttk.Entry(self.input_frame, width=30)
        self.filename_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.filename_entry.insert(0, "output")

        self.analyze_button = ttk.Button(self.input_frame, text="🔍 Phân tích Section ID", command=self.analyze)
        self.analyze_button.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        # Log kết quả
        self.log_text = tk.Text(root, height=15)
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def on_close(self):
        self.root.destroy()
        if self.parent_root:
            self.parent_root.destroy()  


    def analyze(self):
        url = self.url_entry.get().strip()
        filename = self.filename_entry.get().strip()
        self.log_text.delete(1.0, tk.END)

        result = extract_section_ids(url)

        if isinstance(result, str) and result.startswith("error:"):
            self.log_text.insert(tk.END, f"❌ Lỗi: {result[7:]}")
            return

        if isinstance(result, list) and result:
            self.log_text.insert(tk.END, f"✅ Tìm thấy {len(result)} section ID. Đang lưu vào file...\n\n")

            output_folder = "Analyze Output"
            os.makedirs(output_folder, exist_ok=True)

            output_path = os.path.join(output_folder, f"{filename}.csv")

            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["URL", url])
                writer.writerow(["STT", "Section ID"])
                seen = set()
                for i, sid in enumerate(result, 1):
                    if sid not in seen:
                        writer.writerow([i, sid])
                        seen.add(sid)


            self.log_text.insert(tk.END, f"📁 Đã lưu vào: {output_path}")
        else:
            self.log_text.insert(tk.END, "⚠️ Không tìm thấy section ID nào.\n")

    def go_back(self):
        self.root.destroy()
        if self.parent_root:
            self.parent_root.deiconify()
