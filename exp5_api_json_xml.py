# Exp 5: Fetch USGS Earthquakes GeoJSON API and GDACS Disaster RSS XML feed via ElementTree.
import time, requests, xml.etree.ElementTree as ET, pandas as pd

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson"
GDACS_URL = "https://www.gdacs.org/xml/rss.xml"
HEADERS = {"User-Agent": "DisasterWatchBot/1.0 (academic research; contact: student@univ.edu)"}

def fetch_usgs():
    time.sleep(1)
    r = requests.get(USGS_URL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    rows = []
    for f in r.json().get("features", []):
        props, coords = f.get("properties", {}), f.get("geometry", {}).get("coordinates", [None, None])
        rows.append({"source": "USGS", "title": props.get("title", ""), "location": props.get("place", ""), "severity": props.get("mag"), "timestamp": pd.to_datetime(props.get("time"), unit="ms", utc=True), "lon": coords[0], "lat": coords[1], "event_type": "earthquake"})
    df = pd.DataFrame(rows)
    df.to_csv("data/raw_usgs.csv", index=False)
    print(f"[Exp5] Saved {len(df)} USGS earthquake records -> data/raw_usgs.csv")
    return df

def fetch_gdacs():
    time.sleep(1)
    try:
        r = requests.get(GDACS_URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        ns = {"geo": "http://www.w3.org/2003/01/geo/wgs84_pos#", "gdacs": "http://www.gdacs.org", "georss": "http://www.georss.org/georss"}
        rows = []
        for it in root.findall("./channel/item"):
            title, country = it.findtext("title", default=""), it.findtext("gdacs:country", default="", namespaces=ns)
            pt = it.findtext("georss:point", default="", namespaces=ns).strip()
            lat, lon = (float(pt.split()[0]), float(pt.split()[1])) if len(pt.split()) == 2 else (None, None)
            g_lat = it.findtext("geo:lat", default="", namespaces=ns)
            g_lon = it.findtext("geo:long", default="", namespaces=ns) or it.findtext("geo:lon", default="", namespaces=ns)
            if g_lat and g_lon: lat, lon = float(g_lat), float(g_lon)
            if any(k in (title + " " + country).lower() for k in ["bangladesh", "gulf of mexico", "mexico", "united states", "wildfire", "california", "brazil"]):
                print(f"[Exp5 GDACS Raw vs Parsed] '{title[:45]}...' | georss:point='{pt}' | geo:lat='{g_lat}', geo:long='{g_lon}' => lat={lat}, lon={lon}")
            rows.append({"source": "GDACS", "title": title, "location": country, "severity": it.findtext("gdacs:severity", default="", namespaces=ns), "timestamp": it.findtext("pubDate", default=""), "event_type": it.findtext("gdacs:eventtype", default="", namespaces=ns).lower(), "lat": lat, "lon": lon})
        df = pd.DataFrame(rows)
        df.to_csv("data/raw_gdacs.csv", index=False)
        print(f"[Exp5] Saved {len(df)} GDACS disaster records -> data/raw_gdacs.csv")
        return df
    except Exception as e:
        print(f"[Exp5] GDACS RSS error: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    fetch_usgs()
    fetch_gdacs()
