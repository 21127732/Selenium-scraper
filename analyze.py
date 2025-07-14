
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import csv
import os


def extract_section_ids(url):
    """
    Phân tích section ID từ URL. Tự động nhận diện wiki vs doanh nghiệp.
    Nếu là wiki (wiki.gg, wikipedia.org, v.v.) thì phân tích theo id như cũ.
    Nếu là doanh nghiệp thì dò theo các block lớn có nhiều văn bản & liên kết.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        parsed_url = urlparse(url)

        domain = parsed_url.netloc.lower()
        is_wiki = any(kw in domain for kw in ["wiki", "wikipedia"])

        content_div = (
            soup.find("div", id="content")
            or soup.find("div", id="mw-content-text")
            or soup.body
        )

        final_ids = []
        seen_ids = set()

        if is_wiki:
            # --- Cách 1: Tìm các block có id và nhiều liên kết nội bộ ---
            tags_to_check = ["div", "section", "ul", "table", "aside"]
            candidates = []

            for tag in tags_to_check:
                for block in content_div.find_all(tag):
                    block_id = block.get("id")
                    if not block_id:
                        continue

                    links = block.find_all("a", href=True)
                    internal_links = [
                        a for a in links
                        if a["href"].startswith("/wiki") or parsed_url.netloc in a["href"]
                    ]

                    if len(internal_links) >= 2:
                        candidates.append((block_id, block))

            # Loại bỏ block là tổ tiên của block khác
            for i, (id1, block1) in enumerate(candidates):
                is_ancestor = False
                for j, (_, block2) in enumerate(candidates):
                    if i != j and block1 in block2.parents:
                        is_ancestor = True
                        break
                if not is_ancestor and id1 not in seen_ids:
                    final_ids.append(id1)
                    seen_ids.add(id1)

            # --- Cách 2: Thêm tiêu đề có id ---
            heading_tags = content_div.select("h2[id], h3[id], h4[id], h5[id]")
            for tag in heading_tags:
                heading_id = tag.get("id")
                if heading_id and heading_id not in seen_ids:
                    final_ids.append(heading_id)
                    seen_ids.add(heading_id)

        else:
            # Trang doanh nghiệp: tìm các div/section/article chứa nhiều chữ & liên kết
            candidates = []
            tags_to_check = ["section", "div", "article"]

            for tag in tags_to_check:
                for block in content_div.find_all(tag):
                    text_len = len(block.get_text(strip=True))
                    link_count = len(block.find_all("a", href=True))
                    if text_len >= 200 and link_count >= 2:
                        snippet = block.get_text(strip=True)[:50]
                        if snippet not in seen_ids:
                            final_ids.append(snippet)
                            seen_ids.add(snippet)

        return {"type": "wiki", "sections": final_ids}

    except Exception as e:
        return f"error: {e}"
def save_sections_to_csv(url, folder_name, sections):
    if not os.path.exists("Analyze Output"):
        os.makedirs("Analyze Output")

    filename = os.path.join("Analyze Output", f"{folder_name}.csv")
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["URL", url])
        writer.writerow(["TYPE", sections["type"]])
        writer.writerow(["STT", "Section ID"])
        for idx, sec in enumerate(sections["sections"], 1):
            writer.writerow([idx, sec])
    return filename