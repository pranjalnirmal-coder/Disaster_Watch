# Exp 7: Clean schema, validate coordinates/dates, normalize types, deduplicate, and export master dataset.
import os, re, numpy as np, pandas as pd

SCHEMA = ["source", "event_type", "title", "location", "lat", "lon", "coord_quality", "coord_flag", "severity", "timestamp"]
R_MAP = {"kashmir": (34.08, 74.79), "gujarat": (22.25, 71.19), "kutch": (23.73, 69.85), "assam": (26.20, 92.93), "shillong": (25.57, 91.89), "andaman": (11.74, 92.65), "nicobar": (7.0, 93.77), "maharashtra": (19.75, 75.71), "delhi": (28.61, 77.20), "sikkim": (27.53, 88.51), "uttarakhand": (30.06, 79.01), "bengal": (22.98, 87.85), "bihar": (25.09, 85.31), "jharkhand": (23.61, 85.27), "rajasthan": (27.02, 74.21), "madhya": (23.47, 77.94), "chhattisgarh": (21.27, 81.86), "odisha": (20.95, 85.09), "tamil": (11.12, 78.65), "himachal": (31.10, 77.17), "nepal": (28.39, 84.12), "bangladesh": (23.68, 90.35), "pakistan": (30.37, 69.34), "myanmar": (21.91, 95.95)}
KW_RE = re.compile(r"\b(flood|floods|flooding|earthquake|quake|landslide|landslides|cyclone|storm|rain|rains|rainfall|cloudburst|wildfire|fire|disaster|drought|tsunami)\b", re.IGNORECASE)

def normalize_type(v):
    v = str(v).lower()
    for t, keys in [("earthquake", ["earthquake", "quake", "tremor", "eq"]), ("flood", ["flood", "rain", "fl", "landslide", "cloudburst"]), ("cyclone", ["cyclone", "storm", "typhoon", "tc"]), ("wildfire", ["wildfire", "fire", "wf"]), ("drought", ["drought", "dr"])]:
        if any(k in v for k in keys): return t
    return "other"

def clean_and_validate():
    raw_files, dfs, counts = ["raw_static.csv", "raw_dynamic.csv", "raw_multipage.csv", "raw_usgs.csv", "raw_gdacs.csv", "raw_paginated.csv"], [], {}
    if os.path.exists("data/raw_static.csv"):
        d = pd.read_csv("data/raw_static.csv"); counts["raw_static.csv"] = len(d)
        coords = d["region"].apply(lambda r: next((coords for k, coords in R_MAP.items() if k in str(r).lower()), (np.nan, np.nan)))
        d["source"], d["location"], d["event_type"], d["severity"], d["timestamp"] = "Static_Scraper", d.get("region"), d.get("type"), "Historical", d.get("date")
        d["lat"], d["lon"], d["coord_quality"], d["coord_flag"] = [c[0] for c in coords], [c[1] for c in coords], "approx_region", "approx_state_centroid"; dfs.append(d)
    if os.path.exists("data/raw_dynamic.csv"):
        d = pd.read_csv("data/raw_dynamic.csv"); counts["raw_dynamic.csv"] = len(d); d["source"], d["event_type"], d["severity"], d["lat"], d["lon"], d["coord_quality"], d["coord_flag"] = "Dynamic_Selenium", "earthquake", "Live", np.nan, np.nan, "none", "unlocated"; dfs.append(d)
    if os.path.exists("data/raw_multipage.csv"):
        d = pd.read_csv("data/raw_multipage.csv"); counts["raw_multipage.csv"] = len(d); d = d[d["headline"].astype(str).apply(lambda h: bool(KW_RE.search(h)))].copy()
        d["source"], d["title"], d["event_type"], d["severity"], d["lat"], d["lon"], d["coord_quality"], d["coord_flag"] = "Multipage_Crawler", d.get("headline"), d.get("headline").apply(normalize_type), "News", np.nan, np.nan, "none", "unlocated"; dfs.append(d)
    for src in ["raw_usgs.csv", "raw_gdacs.csv", "raw_paginated.csv"]:
        if os.path.exists(f"data/{src}"): d = pd.read_csv(f"data/{src}"); counts[src] = len(d); d["coord_quality"], d["coord_flag"] = "exact", "valid"; dfs.append(d)
    combined = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame(columns=SCHEMA)
    total_before = len(combined)
    for c in SCHEMA:
        if c not in combined.columns: combined[c] = None
    combined = combined[SCHEMA][~combined["title"].isna() & (combined["title"].astype(str).str.strip() != "")].copy()
    parsed_dates = pd.to_datetime(combined["timestamp"], format="mixed", utc=True, errors="coerce")
    bad_dates, combined["timestamp"] = int(parsed_dates.isna().sum()), parsed_dates.fillna(pd.Timestamp.now(tz="UTC"))
    combined["lat"], combined["lon"] = pd.to_numeric(combined["lat"], errors="coerce"), pd.to_numeric(combined["lon"], errors="coerce")
    
    flagged_samples, counts_per_src = [], {}
    for idx, row in combined.iterrows():
        lat, lon, src, title = row["lat"], row["lon"], row["source"], row["title"]
        if pd.isna(lat) or pd.isna(lon): combined.at[idx, "coord_quality"], combined.at[idx, "coord_flag"] = "none", "unlocated"
        elif abs(lat) > 90 and abs(lon) <= 90:
            combined.at[idx, "lat"], combined.at[idx, "lon"], combined.at[idx, "coord_flag"] = lon, lat, "swapped_fixed"
            flagged_samples.append((src, title[:40], f"lat={lat}, lon={lon}", f"lat={lon}, lon={lat}", "Swapped lat/lon fixed")); counts_per_src[src] = counts_per_src.get(src, 0) + 1
        elif (abs(lat) > 90) or (abs(lon) > 180):
            combined.at[idx, "lat"], combined.at[idx, "lon"], combined.at[idx, "coord_quality"], combined.at[idx, "coord_flag"] = np.nan, np.nan, "none", "out_of_bounds"
            flagged_samples.append((src, title[:40], f"lat={lat}, lon={lon}", "NaN, NaN", "Out of bounds dropped")); counts_per_src[src] = counts_per_src.get(src, 0) + 1
    
    print(f"[Exp7] Coordinate Validation: Flagged counts per source: {counts_per_src or '0 invalid raw coordinates'}")
    combined["event_type"] = combined["event_type"].apply(normalize_type)
    before_dedup = len(combined); combined = combined.drop_duplicates(subset=["title", "event_type", "location"]).reset_index(drop=True)
    combined.to_csv("data/master.csv", index=False)
    summary = f"==================================================\nDISASTERWATCH DATA VALIDATION SUMMARY\n==================================================\nRows in per raw file:\n" + "\n".join([f"  - {k}: {v}" for k, v in counts.items()]) + f"\n\nTotal records before cleaning: {total_before}\nRows dropped by validation rule:\n  - Unparseable dates:    {bad_dates}\n  - Duplicate records:    {before_dedup - len(combined)}\n\nFinal Master records stored:   {len(combined)}\nGeocoded Coordinates by Quality:\n{combined['coord_quality'].value_counts().to_string()}\n\nEvent Type Distribution:\n{combined['event_type'].value_counts().to_string()}\n=================================================="
    print(summary); open("data/validation_summary.txt", "w", encoding="utf-8").write(summary); return combined

if __name__ == "__main__":
    clean_and_validate()
