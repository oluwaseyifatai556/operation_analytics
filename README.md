# Restaurant & Food Delivery Operations Analytics

Analysis of 45,593 food delivery orders to evaluate operational performance against
SLA (Service Level Agreement) targets — order volume trends, delivery time performance,
and the operational factors (traffic, weather, city type, seasonality) that drive
late deliveries.

**Skills demonstrated:** Python (Pandas), SQL, data cleaning, KPI definition,
exploratory data analysis, data visualization.

## Business Question

Food delivery and restaurant operations platforms are evaluated on how consistently
they hit delivery-time promises to customers. This project answers:
- How is order volume trending over time?
- What % of orders meet the delivery SLA, and how does that vary by city, traffic,
  weather, and vehicle type?
- Which operational segments are the biggest risk to SLA compliance, and where
  should operations teams focus improvement efforts?

## Dataset

[Food Delivery Dataset](https://www.kaggle.com/datasets/gauravmalik26/food-delivery-dataset)
(Kaggle, Gaurav Malik) — 45,593 food delivery orders across Indian cities, including
order timestamps, delivery time, traffic density, weather conditions, vehicle type,
festival flag, and city classification (Urban / Metropolitan / Semi-Urban).

**SLA definition:** an order is "on-time" if `Time_taken(min) <= 30`. This 30-minute
threshold is a standard food-delivery industry benchmark, documented as an assumption
since the raw dataset doesn't specify a contractual SLA.

## Data Cleaning

The raw file required non-trivial cleaning before analysis — documented in
[`notebooks/01_clean_data.py`](notebooks/01_clean_data.py):

- Whitespace padding on nearly every string field (e.g. `"Snack "`, `"Urban "`)
- Literal `"NaN "` strings instead of true nulls
- Units embedded inside values instead of separate fields (e.g. `"conditions Sunny"`,
  `"(min) 24"`)
- **Mixed date formats within a single column** (`dd-mm-yyyy` and `d/m/yyyy`) — naively
  parsing both with one `pd.to_datetime()` call caused pandas to lock onto a single
  format and silently null out ~46% of rows. Fixed by splitting on separator and
  parsing each format explicitly.
- Out-of-range sanity checks (ratings outside 1–5, delivery ages outside 18–65)

All 45,593 rows were retained after cleaning.

## Key Findings

- **Overall SLA compliance: 70.2%** — average delivery time 26.3 minutes (median 26 min)
- **Traffic is the strongest single driver of lateness:** compliance drops from
  **92.1% in low traffic to 49.4% in jam conditions**
- **Semi-Urban orders (n=164) and Festival-day orders (n=896) missed SLA universally
  (0% compliance)** — these aren't occasional misses, every single order in both
  segments exceeded 30 minutes (Semi-Urban averaging 49.7 min, Festival days 45.5 min).
  This points to a capacity-planning gap rather than random variation.
- **City type matters:** Urban 81.3% vs. Metropolitan 66.7% compliance — larger,
  denser markets underperform despite presumably having more delivery infrastructure
- **Vehicle type:** electric scooters and scooters (75–77% compliance) outperform
  motorcycles (66%) — worth investigating fleet mix by region
- **Worst combined segment:** Semi-Urban + Jam traffic (0% compliance, n=135),
  followed by Metropolitan + Jam traffic (46.2% compliance, n=11,090 — the largest
  at-risk segment by volume)
- Order volume is fairly stable week-to-week (~6,300–7,600/week) with no strong
  weekday/weekend seasonality

## Repo Structure

```
├── data/
│   ├── train.csv              # raw Kaggle data
│   └── train_cleaned.csv      # cleaned, analysis-ready
├── notebooks/
│   ├── 01_clean_data.py       # cleaning pipeline
│   └── 02_eda.py              # EDA + chart generation
├── sql/
│   └── analysis_queries.sql   # 10 SQL queries against SQLite (order volume, SLA by segment)
├── dashboards/
│   └── *.png                  # chart outputs
└── README.md
```

## Tools

Python (Pandas, Matplotlib), SQL (SQLite), Streamlit

## Next Steps

- Build an interactive Streamlit dashboard on top of `train_cleaned.csv` with
  slicers for city, traffic, and weather
- Segment-level root cause analysis for the Semi-Urban and Festival-day SLA failures
