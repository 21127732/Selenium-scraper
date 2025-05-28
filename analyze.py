# analyze.py

import requests
from bs4 import BeautifulSoup

def extract_section_ids(url):
    """
    Trả về danh sách section ID từ trang wiki có div class='mp-box'
    Nếu lỗi xảy ra, trả về chuỗi 'error: <nội dung>'
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        section_ids = [
            div.get("id")
            for div in soup.find_all("div", class_="mp-box")
            if div.get("id")
        ]
        return section_ids

    except Exception as e:
        return f"error: {e}"
