from playwright.sync_api import sync_playwright
import time

START_URL = "https://animedekho.app/epi/sentenced-to-be-a-hero-1x1/"

visited = set()

def scrape_iframes(page, url):
    print(f"\n🔎 Opening: {url}")
    page.goto(url, wait_until="networkidle", timeout=60000)

    # wait for JS-rendered iframe
    page.wait_for_selector("iframe", timeout=60000)

    iframe_links = []
    for iframe in page.query_selector_all("iframe"):
        src = iframe.get_attribute("src")
        if src and src.startswith("http"):
            iframe_links.append(src)
            print("✅ IFRAME:", src)

    return iframe_links


def get_next_episode(page):
    selectors = [
        "a[rel='next']",
        "a.next",
        "a:has-text('Next')",
        "a:has-text('Episode')"
    ]

    for sel in selectors:
        link = page.query_selector(sel)
        if link:
            href = link.get_attribute("href")
            if href and href.startswith("http"):
                print("➡ Next episode:", href)
                return href
    return None


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
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )

    page = context.new_page()

    current_url = START_URL

    while current_url and current_url not in visited:
        visited.add(current_url)

        iframe_links = scrape_iframes(page, current_url)

        # save results
        for link in iframe_links:
            with open("iframe_links.txt", "a", encoding="utf-8") as f:
                f.write(f"{current_url} | {link}\n")

        time.sleep(2)

        current_url = get_next_episode(page)

    browser.close()

print("\n✅ SCRAPING COMPLETED")
