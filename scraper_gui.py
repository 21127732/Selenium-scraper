import tkinter as tk
from tkinter import ttk
from analyze import extract_section_ids


def start_gui(parent_root):
    new_window = tk.Toplevel()
    center_window(new_window, 720, 400)
    app = AnalyzeApp(new_window, parent_root)

def center_window(window, width=720, height=400):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


class AnalyzeApp:
    def __init__(self, root, parent_root=None):
        self.root = root
        self.parent_root = parent_root
        self.root.title("Phân tích Section ID từ URL")
        self.root.geometry("720x400")

        # Nút back
        ttk.Button(root, text="← Quay lại", command=self.go_back).pack(anchor="nw", padx=10, pady=5)

        # Khung nhập
        self.input_frame = ttk.Frame(root)
        self.input_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(self.input_frame, text="🔗 Nhập URL:").grid(row=0, column=0, sticky=tk.W, padx=10)
        self.url_entry = ttk.Entry(self.input_frame, width=70)
        self.url_entry.grid(row=0, column=1, padx=5)
        self.url_entry.insert(0, "https://limbuscompany.wiki.gg/wiki/Limbus_Company_Wiki")

        self.analyze_button = ttk.Button(self.input_frame, text="🔍 Phân tích Section ID", command=self.analyze)
        self.analyze_button.grid(row=0, column=2, padx=10)

        # Log kết quả
        self.log_text = tk.Text(root, height=15)
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def analyze(self):
        url = self.url_entry.get().strip()
        self.log_text.delete(1.0, tk.END)
        result = extract_section_ids(url)

        if isinstance(result, str) and result.startswith("error:"):
            self.log_text.insert(tk.END, f"❌ Lỗi: {result[7:]}")
        elif isinstance(result, list) and result:
            self.log_text.insert(tk.END, f"✅ Tìm thấy {len(result)} section ID:\n\n")
            for i, sid in enumerate(result, 1):
                self.log_text.insert(tk.END, f"{i}. {sid}\n")
        else:
            self.log_text.insert(tk.END, "⚠️ Không tìm thấy section ID nào.\n")

    def go_back(self):
        self.root.destroy()
        if self.parent_root:
            self.parent_root.deiconify()
