from playwright.sync_api import sync_playwright, TimeoutError
import time

def scrape_iframes(page, url):
    print(f"\n🔎 Opening: {url}")

    # IMPORTANT: do NOT use networkidle
    page.goto(url, wait_until="domcontentloaded", timeout=60000)

    # small delay for JS players
    page.wait_for_timeout(3000)

    # Try clicking play button (some sites require this)
    try:
        page.click("button", timeout=3000)
    except:
        pass

    try:
        page.wait_for_selector("iframe", timeout=60000)
    except TimeoutError:
        print("❌ No iframe found")
        return []

    iframe_links = []

    for iframe in page.query_selector_all("iframe"):
        src = iframe.get_attribute("src")
        if src and src.startswith("http"):
            iframe_links.append(src)
            print("✅ IFRAME:", src)

    return iframe_links


def main():
    url = input("Enter URL: ").strip()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            viewport={"width": 1280, "height": 720}
        )

        page = context.new_page()

        iframe_links = scrape_iframes(page, url)

        # Save results
        if iframe_links:
            with open("iframe_links.txt", "a", encoding="utf-8") as f:
                for link in iframe_links:
                    f.write(f"{url} | {link}\n")

        browser.close()

    print("\n✅ SCRAPING DONE")


if __name__ == "__main__":
    main()
