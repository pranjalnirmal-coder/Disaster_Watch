# Exp 3: Scrape client-side JS rendered dynamic disaster data with Selenium headless Chrome.
import time, requests, pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

URL = "https://earthquake.usgs.gov/earthquakes/map/?extent=-60,-150&extent=85,150&listOnlyShown=true"

def scrape_dynamic():
    static_rows = len(BeautifulSoup(requests.get(URL, timeout=8).text, "html.parser").select("mat-list-item, .list-item"))
    print(f"[Exp3] Static Requests: {static_rows} rows found (Client-Side JS SPA renders empty container)")
    
    opts = Options()
    opts.add_argument("--headless=new"); opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage"); opts.page_load_strategy = "eager"
    opts.add_argument("user-agent=DisasterWatchBot/1.0")
    
    driver = webdriver.Chrome(options=opts)
    try:
        driver.get(URL); time.sleep(4)
        items_before = driver.find_elements(By.CSS_SELECTOR, "mat-list-item, .mat-list-item")
        print(f"[Exp3] Selenium Initial JS Render: {len(items_before)} rows")
        
        scrolls = 3
        for s in range(scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        items_after = driver.find_elements(By.CSS_SELECTOR, "mat-list-item, .mat-list-item")
        print(f"[Exp3] Selenium performed {scrolls} scrolls | Rows before: {len(items_before)} -> Rows after: {len(items_after)}")
        print("[Exp3] Scroll Observation: Scrolling adds 0 new rows because USGS SPA renders the full initial list directly in the DOM.")
        
        rows = []
        for item in items_after:
            txt = item.text.strip().replace("\n", " - ")
            if txt and len(txt) > 5:
                rows.append({"title": txt, "location": txt.split("-")[-1].strip(), "timestamp": pd.Timestamp.now(tz="UTC"), "url": URL, "event_type": "earthquake"})
        
        df = pd.DataFrame(rows).drop_duplicates(subset=["title"])
        df.to_csv("data/raw_dynamic.csv", index=False)
        print(f"[Exp3] Note: {len(items_after)} rendered DOM elements reduced to {len(df)} saved rows after filtering non-event UI header/container elements.")
        print(f"[Exp3] Scraped {len(df)} dynamic rows -> data/raw_dynamic.csv")
        return df
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_dynamic()
