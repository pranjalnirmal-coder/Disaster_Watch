# DisasterWatch Interactive Analytics Dashboard built with Streamlit and Plotly.
import os, pandas as pd, plotly.express as px, streamlit as st

st.set_page_config(page_title="DisasterWatch", page_icon="🌍", layout="wide")
st.title("🌍 DisasterWatch: Multi-Source Disaster Data Scraping & Analytics")
if not (os.path.exists("data/master.csv") and os.path.getsize("data/master.csv") > 0):
    st.error("Missing or empty data/master.csv. Run 'python run_all.py' first."); st.stop()

df = pd.read_csv("data/master.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", utc=True)
min_date, max_date = df["timestamp"].min().date(), df["timestamp"].max().date()

st.sidebar.header("🔍 Filters")
sel_types = st.sidebar.multiselect("Event Type", options=df["event_type"].unique(), default=df["event_type"].unique())
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])
start_d, end_d = (date_range[0], date_range[1]) if len(date_range) == 2 else (min_date, max_date)
filtered = df[(df["event_type"].isin(sel_types)) & (df["timestamp"].dt.date >= start_d) & (df["timestamp"].dt.date <= end_d)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Events", len(filtered)); c2.metric("Data Sources", filtered["source"].nunique())
c3.metric("Geocoded Events", filtered[["lat", "lon"]].dropna().shape[0]); c4.metric("Primary Event Type", filtered["event_type"].mode()[0].title() if len(filtered) else "N/A")

st.subheader("🗺️ Global & Regional Disaster Map")
map_df = filtered.dropna(subset=["lat", "lon"])
if len(map_df):
    fig_map = px.scatter_geo(map_df, lat="lat", lon="lon", color="event_type", hover_name="title", hover_data=["location", "coord_quality", "source", "timestamp"], title="Disaster Distribution Map", template="plotly_dark", height=500)
    fig_map.update_geos(showcountries=True, showcoastlines=True, showland=True, fitbounds="locations")
    st.plotly_chart(fig_map, use_container_width=True)

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("📊 Event Count by Type")
    counts = filtered["event_type"].value_counts().reset_index(); counts.columns = ["Event Type", "Count"]
    st.plotly_chart(px.bar(counts, x="Event Type", y="Count", color="Event Type", template="plotly_dark"), use_container_width=True)
with col_b:
    st.subheader("📈 Disaster Frequency Over Time")
    daily = filtered.groupby([filtered["timestamp"].dt.date, "event_type"]).size().reset_index(name="Count")
    st.plotly_chart(px.line(daily, x="timestamp", y="Count", color="event_type", template="plotly_dark"), use_container_width=True)

st.divider(); st.subheader("📖 Mini Case Study: M 6.6 Tadine Earthquake Sequence Timeline")
if os.path.exists("data/case_study.csv") and os.path.getsize("data/case_study.csv") > 0:
    case_df = pd.read_csv("data/case_study.csv"); case_df["timestamp"] = pd.to_datetime(case_df["timestamp"], format="mixed", utc=True)
    d_min, d_max, n_rec = case_df["timestamp"].min().strftime("%B %d, %Y"), case_df["timestamp"].max().strftime("%B %d, %Y"), len(case_df)
    max_m = case_df["magnitude"].max() if "magnitude" in case_df.columns else 6.6
    src_info = ", ".join([f"{count} records from {src}" for src, count in case_df["source"].value_counts().items()])
    st.markdown(f"This case study highlights the **M {max_m:.1f} earthquake and aftershock sequence** recorded near Tadine and the Loyalty Islands, New Caledonia. The timeline comprises **{n_rec} events** tracked between **{d_min}** and **{d_max}**. All records in this sequence were retrieved directly from live feeds ({src_info}). This event was chosen automatically as the single largest disaster cluster available in the master dataset. Historical events like the 2018 Kerala floods could not be used because live API feeds only supply recent 30-day observations.")
    st.plotly_chart(px.scatter(case_df, x="timestamp", y="magnitude" if "magnitude" in case_df.columns else "event_type", color="source", hover_data=["title", "location", "severity"], template="plotly_dark", height=380), use_container_width=True)
    st.dataframe(case_df[["timestamp", "source", "event_type", "title", "location", "severity"]], use_container_width=True, height=220)
else: st.info("Case study data not available yet.")

st.divider(); st.subheader("🌤️ Regional Weather Context (OpenWeatherMap)")
if os.path.exists("data/weather_context.csv") and os.path.getsize("data/weather_context.csv") > 0:
    st.dataframe(pd.read_csv("data/weather_context.csv"), use_container_width=True)
else: st.info("Weather data not available yet. Add OPENWEATHER_API_KEY to .env and run exp6_api_auth.py.")
