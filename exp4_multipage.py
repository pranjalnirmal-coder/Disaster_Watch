# Exp 4: Crawl paginated news with word-boundary disaster filter, retries, timeouts, and logging.
import time, logging, re, requests, pandas as pd
from bs4 import BeautifulSoup

logging.basicConfig(filename="scrape.log", level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", force=True)
BASE_URL = "https://indianexpress.com/section/india/page/{}/"
HEADERS = {"User-Agent": "DisasterWatchBot/1.0 (academic research; contact: student@univ.edu)"}
KW_REGEX = re.compile(r"\b(flood|floods|flooding|earthquake|quake|landslide|landslides|cyclone|storm|rain|rains|rainfall|cloudburst|wildfire|disaster|drought|tsunami)\b", re.IGNORECASE)

def fetch_page(url, timeout=8, max_retries=2):
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"Fetching {url} (Attempt {attempt}/{max_retries})"); time.sleep(1)
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code == 404:
                logging.warning(f"HTTP 404 Not Found for {url} on attempt {attempt}")
                print(f"[Exp4] Handled HTTP 404 Not Found: {url}"); return None
            r.raise_for_status(); return r.text
        except Exception as e:
            logging.warning(f"Error fetching {url} on attempt {attempt}: {e}")
            if attempt == max_retries: logging.error(f"Failed {url} after {max_retries} attempts: {e}"); return None
            time.sleep(1)

def test_error_handling():
    print("[Exp4] Testing deliberate 404 & timeout error handling...")
    fetch_page("https://indianexpress.com/section/india/page/999999_test404/", max_retries=1)
    fetch_page("https://10.255.255.1/test_timeout", timeout=0.05, max_retries=2)

def scrape_multipage(max_pages=10):
    test_error_handling()
    all_rows, seen = [], set()
    for p in range(1, max_pages + 1):
        url, html = BASE_URL.format(p), fetch_page(BASE_URL.format(p))
        page_scraped, page_kept = [], []
        if html:
            for h in BeautifulSoup(html, "html.parser").find_all(["h2", "h3"]):
                a = h.find("a")
                hl, link = (a.get_text(strip=True), a.get("href", "")) if a else ("", "")
                if hl and len(hl) > 15 and link.startswith("http") and hl not in seen:
                    seen.add(hl); item = {"headline": hl, "timestamp": pd.Timestamp.now(tz="UTC"), "location": "India", "url": link}
                    page_scraped.append(item)
                    m = KW_REGEX.search(hl)
                    if m:
                        item["matched_kw"] = m.group(0).lower()
                        print(f"  [Exp4 Page {p} Kept] (kw: '{item['matched_kw']}') -> '{hl}'")
                        page_kept.append(item)
        print(f"[Exp4] Page {p}: URL={url} | Scraped: {len(page_scraped)} | Kept: {len(page_kept)}")
        all_rows.extend(page_kept)
    df = pd.DataFrame(all_rows); df.to_csv("data/raw_multipage.csv", index=False)
    print(f"[Exp4] Multipage Crawl Complete: {len(df)} disaster-relevant rows saved -> data/raw_multipage.csv")
    return df

if __name__ == "__main__":
    scrape_multipage()
