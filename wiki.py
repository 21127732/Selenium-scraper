
import csv
import os
import time
from urllib.parse import urlparse, unquote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def init_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    return driver


def sanitize_filename(url):
    path = urlparse(url).path.split("/")[-1]
    return unquote(path).replace(" ", "_").replace(":", "_")


def wait_for_page(driver, wait_time=10):
    WebDriverWait(driver, wait_time).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def list_unique_links_from_section(driver, url: str, section_id: str, name: str, headless, scrape):
    try:
        print(f"🔗 Đang truy cập: {url}")
        driver.get(url)

        if headless:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, section_id))
            )
        else:
            wait_for_page(driver, 10)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, section_id))
            )

        section = driver.find_element(By.ID, section_id)
        link_elements = section.find_elements(By.TAG_NAME, "a")

        unique_links = {}
        for link in link_elements:
            href = link.get_attribute("href")
            text = link.get_attribute("title") or link.text.strip()
            if href and text and href not in unique_links:
                unique_links[href] = text

        folder_path = os.path.join(os.getcwd(), name)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{name}.csv")

        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for idx, (_, text) in enumerate(unique_links.items(), 1):
                writer.writerow([f"{idx}. {text}"])

        print(f"📁 Đã lưu {len(unique_links)} mục vào file: {file_path}")

        if scrape:
            for href, text in unique_links.items():
                filename = sanitize_filename(text) + ".png"
                image_path = os.path.join(folder_path, filename)

                print(f"📸 Đang vào {text} → {href}")
                driver.get(href)

                wait_for_page(driver, wait_time=10)
                time.sleep(3)

                driver.save_screenshot(image_path)
                print(f"✅ Đã chụp hình: {image_path}")

                driver.get(url)
                wait_for_page(driver, wait_time=10)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, section_id))
                )

    except Exception as e:
        print(f"❌ Lỗi tại mục {name}: {e}")


def quit_driver(driver):
    driver.quit()


# ==== MAIN ====
headless_mode = True
scrape_mode = True

# Tự động vô hiệu hóa chế độ scrape nếu headless được bật
if headless_mode and scrape_mode:
    print("⚠️ Headless mode đang bật — tự động tắt scrape mode để tránh lỗi hiển thị không đầy đủ.")
    scrape_mode = False

driver = init_driver(headless=headless_mode)

list_unique_links_from_section(
    driver,
    url="https://limbuscompany.wiki.gg/wiki/Limbus_Company_Wiki",
    section_id="mp-box-welcome",
    name="Welcome",
    headless=headless_mode,
    scrape=scrape_mode
)

list_unique_links_from_section(
    driver,
    url="https://limbuscompany.wiki.gg/wiki/Limbus_Company_Wiki",
    section_id="mp-box-about",
    name="About",
    headless=headless_mode,
    scrape=scrape_mode
)

list_unique_links_from_section(
    driver,
    url="https://limbuscompany.wiki.gg/wiki/Limbus_Company_Wiki",
    section_id="mp-box-featured",
    name="Featured",
    headless=headless_mode,
    scrape=scrape_mode
)

quit_driver(driver)
