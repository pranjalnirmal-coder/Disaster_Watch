# Exp 6: Real API pagination (USGS fdsnws India bounding box) and authenticated weather context.
import os, sys, time, requests, json, pandas as pd

def mask_key(k): return f"{k[:4]}***{k[-3:]}" if len(k) > 7 else "***"

def fetch_paginated_api(pages=3, limit=5):
    base_url, rows = "https://earthquake.usgs.gov/fdsnws/event/1/query", []
    for p in range(1, pages + 1):
        params = {"format": "geojson", "minlatitude": 6, "maxlatitude": 36, "minlongitude": 68, "maxlongitude": 98, "limit": limit, "offset": (p - 1) * limit + 1}
        r = requests.get(base_url, params=params, timeout=12)
        features = r.json().get("features", []) if r.status_code == 200 else []
        for f in features:
            pr, co = f.get("properties", {}), f.get("geometry", {}).get("coordinates", [None, None])
            rows.append({"source": "USGS_Paginated", "title": pr.get("title", ""), "location": pr.get("place", ""), "severity": pr.get("mag"), "timestamp": pd.to_datetime(pr.get("time"), unit="ms", utc=True), "lat": co[1], "lon": co[0], "event_type": "earthquake"})
        print(f"[Exp6 Page {p}/{pages}] Params: {params} | Rows Returned: {len(features)}"); time.sleep(1)
    df = pd.DataFrame(rows).drop_duplicates(subset=["title"])
    df.to_csv("data/raw_paginated.csv", index=False)
    print(f"[Exp6] Saved {len(df)} distinct paginated records -> data/raw_paginated.csv"); return df

def fetch_weather_context():
    csv_p = "data/weather_context.csv"
    if os.path.exists(csv_p) and os.path.getsize(csv_p) == 0: os.remove(csv_p)
    owm_key = ""
    if os.path.exists(".env"):
        for l in open(".env"):
            if "=" in l and not l.startswith("#"):
                k, v = l.strip().split("=", 1)
                if k.strip() == "OPENWEATHER_API_KEY": owm_key = v.strip()
    is_set, k_len = bool(owm_key), len(owm_key)
    is_placeholder = any(p in owm_key.lower() for p in ["demo", "your_", "xxx"]) or (0 < k_len < 20)
    print(f"[Exp6 Key Audit] OPENWEATHER_API_KEY set: {is_set} | Key Length: {k_len} | Is Placeholder: {is_placeholder}")
    if not is_set or is_placeholder:
        print("[Exp6] Status: BLOCKED ON USER KEY\n[Exp6] Reason: Valid OpenWeatherMap API key missing in .env (do not touch weather_context.csv).\n[Exp6] Action Required: Add 'OPENWEATHER_API_KEY=<valid_32_char_key>' to .env to fetch live weather.")
        sys.exit(2)
    
    cities, rows = [("Kochi", 9.93, 76.26), ("Guwahati", 26.14, 91.73), ("Bhubaneswar", 20.29, 85.82), ("Delhi", 28.61, 77.20)], []
    print(f"[Exp6 Keyed Request] Masked URL: https://api.openweathermap.org/data/2.5/weather?q=Kochi,IN&appid={mask_key(owm_key)}\n[Exp6 Endpoint] /data/2.5/weather (Current Weather endpoint: returns 1 observation per city)")
    for city, lat, lon in cities:
        try:
            r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={owm_key}", timeout=10)
            print(f"[Exp6] City: {city} | HTTP Status: {r.status_code}")
            if r.status_code == 200:
                d = r.json()
                if city == "Kochi": print(f"[Exp6 JSON Sample] {json.dumps({'weather': d.get('weather'), 'main': d.get('main')})}")
                rows.append({"city": city, "weather_condition": d.get("weather", [{}])[0].get("description", ""), "temp_c": round(d.get("main", {}).get("temp", 273.15) - 273.15, 1), "humidity": d.get("main", {}).get("humidity"), "wind_speed": d.get("wind", {}).get("speed"), "lat": lat, "lon": lon, "timestamp": pd.Timestamp.now(tz="UTC")})
        except Exception as e: print(f"[Exp6] Error querying {city}: {e}")
        time.sleep(1)
    if len(rows) > 0:
        df = pd.DataFrame(rows).drop_duplicates(subset=["city"]); df.to_csv(csv_p, index=False)
        print(f"[Exp6] Saved {len(df)} weather context rows -> {csv_p}"); return df
    else:
        print("[Exp6] Status: BLOCKED (No successful HTTP 200 responses; weather_context.csv not created)")
        return pd.DataFrame()

if __name__ == "__main__":
    fetch_paginated_api()
    fetch_weather_context()
