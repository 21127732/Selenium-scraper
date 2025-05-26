
from scraper import init_driver, list_unique_links_from_section, quit_driver

def main():
    headless_mode = False
    scrape_mode = True

    if headless_mode and scrape_mode:
        print("⚠️ Headless mode đang bật — tự động tắt scrape mode để tránh lỗi hiển thị không đầy đủ.")
        scrape_mode = False

    driver = init_driver(headless=headless_mode)


    # https://limbuscompany.wiki.gg/wiki/Limbus_Company_Wiki
    # mp-box-about
    # About
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

if __name__ == "__main__":
    main()
