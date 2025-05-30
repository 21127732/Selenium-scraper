import tkinter as tk
from tkinter import ttk, messagebox
from scraper import init_driver, list_unique_links_from_section, quit_driver

class SectionInput:
    def __init__(self, master, index, remove_callback):
        self.frame = ttk.Frame(master)
        self.index = index
        self.remove_callback = remove_callback

        self.url_entry = ttk.Entry(self.frame, width=60)
        self.section_id_entry = ttk.Entry(self.frame, width=60)
        self.name_entry = ttk.Entry(self.frame, width=60)

        ttk.Label(self.frame, text="URL:").grid(row=0, column=1, sticky=tk.W, padx=30)
        self.url_entry.grid(row=0, column=2, padx=5, pady=2)
        self.url_entry.insert(0, "https://limbuscompany.wiki.gg/wiki/Limbus_Company_Wiki")

        ttk.Label(self.frame, text="Section ID:").grid(row=1, column=1, sticky=tk.W, padx=30)
        self.section_id_entry.grid(row=1, column=2, padx=5, pady=2)

        ttk.Label(self.frame, text="Tên thư mục lưu:").grid(row=2, column=1, sticky=tk.W, padx=30)
        self.name_entry.grid(row=2, column=2, padx=5, pady=2)

        # Dù mục đầu không có nút trừ, vẫn tạo 1 ô trống giữ chỗ để layout không lệch
        if self.index == 0:
            self.placeholder = tk.Label(self.frame, width=2)
            self.placeholder.grid(row=0, column=0, rowspan=3, padx=(5, 5))
        else:
            self.remove_button = tk.Button(self.frame, text="➖", fg="red", width=2, command=self.remove)
            self.remove_button.grid(row=0, column=0, rowspan=3, padx=(0, 5), sticky="n")

    def remove(self):
        self.frame.destroy()
        self.remove_callback(self)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def get_data(self):
        return {
            "url": self.url_entry.get(),
            "section_id": self.section_id_entry.get(),
            "name": self.name_entry.get()
        }

class ScraperApp:
    def on_headless_toggle(self):
        if self.headless_var.get():
            self.scrape_check.state(["disabled"])
        else:
            self.scrape_check.state(["!disabled"])

    def __init__(self, root):
        self.root = root
        self.root.title("Wiki Scraper - Nhiều mục")
        self.root.geometry("720x600")

        self.section_container = ttk.Frame(root)
        self.section_container.pack(padx=10, pady=10, fill=tk.X)
        self.checkbox_frame = ttk.Frame(root)
        self.checkbox_frame.pack(pady=(0, 10), fill=tk.X)


        self.headless_var = tk.BooleanVar(value=True)
        self.scrape_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            self.checkbox_frame,
            text="Chạy chế độ headless",
            variable=self.headless_var,
            command=self.on_headless_toggle
        ).grid(row=0, column=0, sticky="w", padx=120)

        self.scrape_check = ttk.Checkbutton(
            self.checkbox_frame,
            text="Chụp ảnh từng link (scrape)",
            variable=self.scrape_var
        )
        self.scrape_check.grid(row=1, column=0, sticky="w", padx=120, pady=(10, 0))



        self.on_headless_toggle()


        self.sections = []
        self.add_section()

        # Nút +
        self.add_button = tk.Button(root, text="➕", fg="green", width=2, command=self.add_section)
        self.add_button.place(relx=1.0, x=-50, y=10, anchor="ne")
        
        self.run_button = ttk.Button(root, text="🚀 Bắt đầu chạy", command=self.run_scrape)
        self.run_button.pack(pady=10)

        self.log_text = tk.Text(root, height=12)
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def add_section(self):
        if len(self.sections) >= 3:
            return

        section = SectionInput(self.section_container, len(self.sections), self.remove_section)
        section.grid(row=len(self.sections), column=0, pady=10, sticky=tk.W)
        self.sections.append(section)

        if len(self.sections) >= 3:
            self.add_button.config(state = tk.DISABLED, fg = "gray")

        

    def remove_section(self, section):
        if len(self.sections) <= 1:
            messagebox.showinfo("Bắt buộc", "Phải có ít nhất 1 mục.")
            return
        self.sections.remove(section)
        self.relayout_sections()

        self.add_button.config(state=tk.NORMAL, fg="green")

    def relayout_sections(self):
        for idx, sec in enumerate(self.sections):
            sec.grid(row=idx, column=0, pady=10, sticky=tk.W)

    def run_scrape(self):
        self.log_text.delete(1.0, tk.END)
        headless = self.headless_var.get()
        scrape = self.scrape_var.get()

        if headless and scrape:
            scrape = False
            self.log_text.insert(tk.END, "⚠️ Headless đang bật — tự động tắt chế độ chụp ảnh.\n")

        driver = init_driver(headless=headless)

        for i, sec in enumerate(self.sections):
            data = sec.get_data()
            if not data["url"] or not data["section_id"] or not data["name"]:
                self.log_text.insert(tk.END, f"❌ Mục #{i+1} thiếu thông tin. Bỏ qua.\n")
                continue

            self.log_text.insert(tk.END, f"▶️ Đang chạy mục #{i+1}: {data['name']}\n")
            list_unique_links_from_section(
                driver=driver,
                url=data["url"],
                section_id=data["section_id"],
                name=data["name"],
                headless=headless,
                scrape=scrape
            )
        quit_driver(driver)
        self.log_text.insert(tk.END, "✅ Hoàn tất toàn bộ.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperApp(root)
    root.mainloop()
