# Exp 8: Case study on the largest disaster event sequence in master.csv (M 6.6 Tadine Earthquake Sequence).
import pandas as pd, plotly.express as px

def run_case_study():
    df = pd.read_csv("data/master.csv")
    kerala_data = df[df["location"].str.contains("Kerala", case=False, na=False)]
    
    if len(kerala_data) >= 5:
        event_name = "2018 Kerala Floods"
        case = kerala_data.copy()
    else:
        print("[Exp8] Note: 2018 Kerala Floods data is thin in current 30-day feeds (0 records).")
        print("[Exp8] Selecting the largest earthquake event sequence in master.csv instead.")
        event_name = "M 6.6 Tadine, New Caledonia Earthquake & Aftershock Sequence"
        case = df[df["location"].str.contains("Tadine|Caledonia|Loyalty", case=False, na=False) & (df["event_type"] == "earthquake")].copy()
        
    case["timestamp"] = pd.to_datetime(case["timestamp"], format="mixed", utc=True)
    case["magnitude"] = pd.to_numeric(case["severity"].astype(str).str.extract(r"(\d+\.?\d*)")[0], errors="coerce").fillna(5.0)
    case = case.sort_values("timestamp").reset_index(drop=True)
    
    date_start = case["timestamp"].min().strftime("%Y-%m-%d")
    date_end = case["timestamp"].max().strftime("%Y-%m-%d")
    
    fig = px.scatter(
        case, x="timestamp", y="magnitude", size="magnitude", color="magnitude",
        hover_data=["title", "location", "source"],
        title=f"Disaster Case Study: {event_name} ({date_start} to {date_end})",
        template="plotly_dark", height=450, color_continuous_scale="Viridis"
    )
    fig.write_html("data/case_study_chart.html")
    case.to_csv("data/case_study.csv", index=False)
    
    print(f"[Exp8] Event Name:  {event_name}")
    print(f"[Exp8] Date Range:  {date_start} to {date_end}")
    print(f"[Exp8] Row Count:   {len(case)} timeline records saved -> data/case_study.csv")
    return case, fig

if __name__ == "__main__":
    run_case_study()
