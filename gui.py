
import tkinter as tk
from tkinter import ttk, messagebox
from scraper import init_driver, list_unique_links_from_section, quit_driver


def on_headless_toggle():
    if headless_var.get():
        scrape_check.state(["disabled"])
    else:
        scrape_check.state(["!disabled"])


def run_scraper():
    log_text.delete(1.0, tk.END)

    url = url_entry.get()
    section_id = section_id_entry.get()
    name = name_entry.get()
    headless = headless_var.get()
    scrape = scrape_var.get()

    if not url or not section_id or not name:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ các trường!")
        return

    if headless and scrape:
        scrape = False
        log_text.insert(tk.END, "⚠️ Headless đang bật — tự động tắt chế độ chụp ảnh.")

    log_text.insert(tk.END, f"▶️ Bắt đầu chạy với '{name}'...")

    try:
        driver = init_driver(headless=headless)
        list_unique_links_from_section(
            driver=driver,
            url=url,
            section_id=section_id,
            name=name,
            headless=headless,
            scrape=scrape
        )
        quit_driver(driver)
        log_text.insert(tk.END, "✅ Hoàn tất.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")


# Giao diện
root = tk.Tk()
root.title("Wiki Scraper GUI")
root.geometry("680x480")  # Đặt kích thước mặc định mong muốn

frame = ttk.Frame(root, padding=15)
frame.pack(fill=tk.BOTH, expand=True)

# URL
ttk.Label(frame, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=5)
url_entry = ttk.Entry(frame, width=65)
url_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
url_entry.insert(0, "https://limbuscompany.wiki.gg/wiki/Limbus_Company_Wiki")

# Section ID
ttk.Label(frame, text="Section ID:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=5)
section_id_entry = ttk.Entry(frame, width=65)
section_id_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
section_id_entry.insert(0, "mp-box-welcome")

# Folder Name
ttk.Label(frame, text="Tên thư mục lưu:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=5)
name_entry = ttk.Entry(frame, width=65)
name_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
name_entry.insert(0, "Welcome")

# Checkboxes
headless_var = tk.BooleanVar(value=True)
scrape_var = tk.BooleanVar(value=True)

ttk.Checkbutton(
    frame,
    text="Chạy chế độ headless",
    variable=headless_var,
    command=on_headless_toggle
).grid(row=3, column=0, columnspan=2, pady=(20, 0), padx=(20,0), sticky=tk.W)

scrape_check = ttk.Checkbutton(
    frame,
    text="Chụp ảnh từng link (scrape)",
    variable=scrape_var
)
scrape_check.grid(row=4, column=0, columnspan=2, pady=(5, 10), padx=(20,0), sticky=tk.W)


# Button giữa
button_frame = ttk.Frame(frame)
button_frame.grid(row=5, column=0, columnspan=2, pady=15)
ttk.Button(button_frame, text="🚀 Bắt đầu chạy", command=run_scraper).pack()

# Log
log_text = tk.Text(frame, height=10)
log_text.grid(row=6, column=0, columnspan=2, pady=10)

on_headless_toggle()  # Cập nhật trạng thái ban đầu

root.mainloop()
