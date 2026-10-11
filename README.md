# DisasterWatch: Multi-Source Disaster Data Scraping & Analytics

DisasterWatch is an automated 8-stage pipeline collecting Indian and global disaster data.
- **Exp 1-4**: Wikipedia reference scraping, selector audit (find_all/CSS/XPath), Selenium JS render demo (USGS map), and 10-page disaster-filtered news crawl.
- **Exp 5-6**: USGS GeoJSON / GDACS RSS XML APIs, USGS fdsnws 3-page pagination, and OpenWeatherMap authenticated weather context.
- **Exp 7-8**: Schema cleaning (master.csv) and M 6.6 Tadine sequence timeline case study.

## Setup & Execution
1. Add `OPENWEATHER_API_KEY` to `.env` (copied from `.env.example`).
2. Run pipeline: `python run_all.py`
3. Launch dashboard: `python -m streamlit run app.py`

## Limitations
ReliefWeb needs a registered appname (HTTP 403); Exp 6 is BLOCKED ON USER KEY until a valid key is added; Wikipedia uses approximate state centroids; unlocated news items have NaN coordinates; small news sample; case study uses the largest live sequence instead of Kerala 2018.
