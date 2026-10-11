# Exp 1: Scrape static Indian disaster advisory data using Requests and BeautifulSoup.
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/wiki/List_of_earthquakes_in_India"
BACKUP_URL = "https://ndma.gov.in/"
HEADERS = {"User-Agent": "DisasterWatchBot/1.0 (academic research; contact: student@univ.edu)"}

def scrape_static():
    time.sleep(1)
    try:
        r = requests.get(URL, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", class_="wikitable")
        rows = []
        if table:
            for tr in table.find_all("tr")[1:]:
                tds = tr.find_all(["td", "th"])
                if len(tds) >= 3:
                    date = tds[0].get_text(strip=True)
                    region = tds[1].get_text(strip=True)
                    mag = tds[2].get_text(strip=True)
                    damage = tds[6].get_text(strip=True) if len(tds) > 6 else ""
                    title = f"{mag} Earthquake in {region}" if mag else f"Earthquake in {region}"
                    if damage:
                        title += f" - {damage[:40]}"
                    rows.append({"title": title, "date": date, "region": region, "type": "earthquake"})
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv("data/raw_static.csv", index=False)
            print(f"[Exp1] Scraped {len(df)} rows from {URL} -> data/raw_static.csv")
            return df
    except Exception as e:
        print(f"[Exp1] Primary URL failed ({e}), switching to backup...")
    
    # Backup: NDMA
    r = requests.get(BACKUP_URL, headers=HEADERS, timeout=10, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    rows = []
    for a in soup.find_all("a"):
        txt, href = a.get_text(strip=True), a.get("href", "")
        if any(k in href.lower() for k in ["cyclone", "flood", "earthquake", "guidelines"]):
            rows.append({"title": txt or href, "date": "2024-01-01", "region": "India", "type": "advisory"})
    df = pd.DataFrame(rows)
    df.to_csv("data/raw_static.csv", index=False)
    print(f"[Exp1] Scraped {len(df)} rows from backup {BACKUP_URL} -> data/raw_static.csv")
    return df

if __name__ == "__main__":
    scrape_static()
