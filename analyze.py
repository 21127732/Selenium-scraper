
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import csv
import os


def extract_section_ids(url):
    """
    Tìm các block có id nằm TRONG div id="content", chứa nhiều <a> nội bộ,
    và không phải là tổ tiên của các block tương tự.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        parsed_url = urlparse(url)

        content_div = soup.find("div", id="content")
        if not content_div:
            return []

        candidates = []
        seen_ids = set()
        tags_to_check = ["div", "section", "ul", "table", "aside"]

        for tag in tags_to_check:
            for block in content_div.find_all(tag):
                block_id = block.get("id")
                if not block_id:
                    continue  # Bỏ qua nếu không có id

                links = block.find_all("a", href=True)
                internal_links = [
                    a for a in links
                    if a["href"].startswith("/wiki") or parsed_url.netloc in a["href"]
                ]

                if len(internal_links) >= 2:
                    candidates.append((block_id, block))

        # Loại bỏ block là tổ tiên của block khác
        final_ids = []
        for i, (id1, block1) in enumerate(candidates):
            is_ancestor = False
            for j, (_, block2) in enumerate(candidates):
                if i != j and block1 in block2.parents:
                    is_ancestor = True
                    break
            if not is_ancestor and id1 not in seen_ids:
                final_ids.append(id1)
                seen_ids.add(id1)

        return final_ids

    except Exception as e:
        return f"error: {e}"


def save_sections_to_csv(url, folder_name, sections):
    if not os.path.exists("Analyze Output"):
        os.makedirs("Analyze Output")

    filename = os.path.join("Analyze Output", f"{folder_name}.csv")
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["URL", url])
        writer.writerow(["STT", "Section ID"])
        for idx, sec in enumerate(sections, 1):
            writer.writerow([idx, sec])
    return filename
