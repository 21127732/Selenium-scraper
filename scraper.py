
import csv
import os
import time
import threading
from urllib.parse import unquote
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk


def init_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def sanitize_filename(text: str) -> str:
    return unquote(text).replace(" ", "_").replace(":", "_")


def wait_for_page(driver, wait_time=10):
    WebDriverWait(driver, wait_time).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def create_tour_popup(root):
    popup = tk.Toplevel(root)
    popup.title("Tour Mode")
    popup.geometry("400x100")
    popup.attributes("-topmost", True)
    popup.resizable(False, False)
    popup.protocol("WM_DELETE_WINDOW", lambda: None)

    label = tk.Label(
        popup,
        text="🧭 Tour Mode đang chạy\nẤn Enter trong trình duyệt để tiếp tục",
        font=("Arial", 11)
    )
    label.pack(pady=20)
    return popup


def inject_browser_enter_handler(driver):
    driver.execute_script("""
        window.continueTour = false;
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                window.continueTour = true;
            }
        });
    """)


def wait_for_enter_in_browser(driver, timeout=120):
    driver.execute_script("""
        window.continueTour = false;
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                window.continueTour = true;
            }
        }, { once: true });
    """)
    for _ in range(timeout * 2):
        flag = driver.execute_script("return window.continueTour === true")
        if flag:
            return
        time.sleep(0.5)



def list_unique_links_from_section(driver, url: str, section_id: str, name: str,
                                    headless=True, photo=False, tour=False, parent_window=None):
    try:
        print(f"🔗 Đang truy cập: {url}")
        driver.get(url)
        wait_for_page(driver)

        try:
            section = driver.find_element(By.ID, section_id)
        except Exception:
            return "invalid_section"

        link_elements = section.find_elements(By.TAG_NAME, "a")
        unique_links = {}
        for link in link_elements:
            href = link.get_attribute("href")
            text = link.get_attribute("title") or link.text.strip()
            if href and text and href not in unique_links:
                unique_links[href] = text

        if not unique_links:
            return "no_links"

        output_base = "Scrape Output"
        folder_path = os.path.join(output_base, name)
        os.makedirs(folder_path, exist_ok=True)

        csv_path = os.path.join(folder_path, f"{name}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["STT", "Tên Mục", "URL"])
            for idx, (href, text) in enumerate(unique_links.items(), 1):
                writer.writerow([idx, text, href])

        print(f"📁 Đã lưu {len(unique_links)} liên kết vào {csv_path}")

        # Hiển thị popup duy nhất trong Tour Mode
        popup = None
        if tour and parent_window:
            popup = tk.Toplevel(parent_window)
            popup.title("Tour Mode")
            popup.geometry("400x100")
            popup.attributes("-topmost", True)
            popup.resizable(False, False)
            popup.protocol("WM_DELETE_WINDOW", lambda: None)

            label = tk.Label(
                popup,
                text="🧭 Tour Mode đang chạy\nẤn Enter trong trình duyệt để tiếp tục",
                font=("Arial", 11)
            )
            label.pack(pady=20)
            popup.update()

        # Bắt đầu chạy từng link
        if photo or tour:
            inject_browser_enter_handler(driver)

            for href, text in unique_links.items():
                print(f"🌐 Đang mở {text}")
                driver.get(href)
                wait_for_page(driver)
                time.sleep(1.5)

                if photo:
                    img_name = sanitize_filename(text) + ".png"
                    img_path = os.path.join(folder_path, img_name)
                    driver.save_screenshot(img_path)
                    print(f"✅ Đã chụp ảnh {img_path}")

                if tour:
                    wait_for_enter_in_browser(driver)

                driver.get(url)
                wait_for_page(driver)

        if popup:
            try:
                popup.destroy()
            except:
                pass

        return "success"

    except Exception as e:
        print(f"❌ Lỗi xảy ra: {e}")
        return "error"

def quit_driver(driver):
    driver.quit()
