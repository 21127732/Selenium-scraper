
import csv
import os
import time
from urllib.parse import urlparse, unquote
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
import threading


def init_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


def sanitize_filename(text: str) -> str:
    return unquote(text).replace(" ", "_").replace(":", "_")


def wait_for_page(driver, wait_time=10):
    WebDriverWait(driver, wait_time).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def wait_for_user_continue(parent_window):
    proceed_event = threading.Event()

    def proceed():
        proceed_event.set()
        popup.destroy()

    popup = tk.Toplevel(parent_window)
    popup.title("Tour Mode")
    popup.geometry("350x120")
    popup.attributes("-topmost", True)
    popup.resizable(False, False)

    label = tk.Label(popup, text="🧭 Tour Mode\nẤn Enter hoặc nút dưới để tiếp tục", font=("Arial", 11))
    label.pack(pady=10)

    btn = tk.Button(popup, text="Tiếp tục", command=proceed)
    btn.pack(pady=5)

    popup.bind("<Return>", lambda e: proceed())

    popup.grab_set()
    popup.wait_window()

    proceed_event.wait()


def list_unique_links_from_section(driver, url: str, section_id: str, name: str, headless=True, photo=False, tour=False, parent_window=None):
    try:
        print(f"🔗 Đang truy cập: {url}")
        driver.get(url)
        wait_for_page(driver)

        # Tìm section theo ID
        try:
            section = driver.find_element(By.ID, section_id)
        except Exception:
            return "invalid_section"

        # Tìm và lọc các liên kết duy nhất
        link_elements = section.find_elements(By.TAG_NAME, "a")
        unique_links = {}
        for link in link_elements:
            href = link.get_attribute("href")
            text = link.get_attribute("title") or link.text.strip()
            if href and text and href not in unique_links:
                unique_links[href] = text

        if not unique_links:
            return "no_links"

        # Tạo thư mục chứa kết quả
        output_base = "Scrape Output"
        folder_path = os.path.join(output_base, name)
        os.makedirs(folder_path, exist_ok=True)

        # Ghi CSV
        csv_path = os.path.join(folder_path, f"{name}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["STT", "Tên Mục", "URL"])
            for idx, (href, text) in enumerate(unique_links.items(), 1):
                writer.writerow([idx, text, href])

        print(f"📁 Đã lưu {len(unique_links)} liên kết vào {csv_path}")

        # Nếu có chụp ảnh / tour
        if photo or tour:
            for href, text in unique_links.items():
                print(f"🌐 Đang mở {text}")
                driver.get(href)
                wait_for_page(driver)
                time.sleep(1)

                if tour and parent_window:
                    wait_for_user_continue(parent_window)

                if photo:
                    img_name = sanitize_filename(text) + ".png"
                    img_path = os.path.join(folder_path, img_name)
                    driver.save_screenshot(img_path)
                    print(f"✅ Đã chụp ảnh {img_path}")

                driver.get(url)
                wait_for_page(driver)


        return "success"

    except Exception as e:
        print(f"❌ Lỗi xảy ra: {e}")
        return "error"



def quit_driver(driver):
    driver.quit()
