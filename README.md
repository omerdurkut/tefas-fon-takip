# TEFAS Fund Tracker

A Python learning project that pulls historical fund data from TEFAS
(Turkey's Electronic Fund Trading Platform) and visualizes it for
comparison across fund categories.

## Contents

- `fon_cek.py` — Fetches historical price data for a single fund and
  plots it.
- `fon_karsilastir.py` — Compares multiple funds on an indexed basis
  (start = 100), producing a summary table and a comparison chart.
- `app.py` — Interactive dashboard built with Streamlit, running in
  the browser.

## Setup

\`\`\`
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

## Usage

\`\`\`
python fon_cek.py              # single fund
python fon_karsilastir.py      # multi-fund comparison
streamlit run app.py           # interactive dashboard
\`\`\`

## What I learned

- TEFAS's undocumented API changed over time, and how a maintained
  community library (tefas-crawler) solved that fragility
- Data cleaning and transformation with pandas
- Building a quick interactive interface with Streamlit
