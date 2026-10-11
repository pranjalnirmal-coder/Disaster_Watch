# Exp 2: Extract the same fields three ways (find_all, CSS select, XPath via lxml) and compare results.
import time
import requests
from bs4 import BeautifulSoup
from lxml import html

URL = "https://en.wikipedia.org/wiki/List_of_earthquakes_in_India"
HEADERS = {"User-Agent": "DisasterWatchBot/1.0 (academic research; contact: student@univ.edu)"}

def compare_selectors():
    time.sleep(1)
    r = requests.get(URL, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    tree = html.fromstring(r.content)

    # 1. BeautifulSoup find_all
    t1 = soup.find("table", class_="wikitable")
    res_findall = []
    if t1:
        for tr in t1.find_all("tr")[1:]:
            tds = tr.find_all(["td", "th"])
            if len(tds) >= 3:
                res_findall.append((tds[0].get_text(strip=True), tds[1].get_text(strip=True), tds[2].get_text(strip=True)))

    # 2. CSS Selectors
    res_css = []
    for tr in soup.select("table.wikitable tr")[1:]:
        tds = tr.select("td, th")
        if len(tds) >= 3:
            res_css.append((tds[0].get_text(strip=True), tds[1].get_text(strip=True), tds[2].get_text(strip=True)))

    # 3. XPath via lxml
    trs = tree.xpath("//table[contains(@class, 'wikitable')]//tr[position()>1]")
    res_xpath = []
    for tr in trs:
        tds = tr.xpath("./td | ./th")
        if len(tds) >= 3:
            res_xpath.append((tds[0].text_content().strip(), tds[1].text_content().strip(), tds[2].text_content().strip()))

    print(f"[Exp2] Selector Extraction Comparison for {URL}:")
    print(f"  - BeautifulSoup find_all: {len(res_findall)} items (Sample: {res_findall[0] if res_findall else 'None'})")
    print(f"  - CSS Selectors (select): {len(res_css)} items (Sample: {res_css[0] if res_css else 'None'})")
    print(f"  - XPath via lxml:         {len(res_xpath)} items (Sample: {res_xpath[0] if res_xpath else 'None'})")
    print(f"  - Consistency: {'ALL 3 METHODS MATCH' if len(res_findall) == len(res_css) == len(res_xpath) else 'DISCREPANCY FOUND'}")
    return {"find_all_count": len(res_findall), "css_count": len(res_css), "xpath_count": len(res_xpath)}

if __name__ == "__main__":
    compare_selectors()
