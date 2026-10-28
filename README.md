# 🎮 GamePulse Intelligence — Nintendo Edition

A Nintendo-first, source-transparent business intelligence portfolio project. **Independent educational project; not affiliated with or endorsed by Nintendo.**

## Features (v0.2 — playful interface)

- Nintendo-inspired visual design with friendly headings, warm off-white surfaces, bright red, sunshine yellow, sky blue, and mint accents. No official brand assets or character art are used.
- Three navigable dashboard areas: **Console quest**, **Games & genres**, and **Data guide**.
- Interactive Plotly comparisons, colorful ranked-game charts, an explicitly sample-only genre donut, selectable reporting checkpoints, and CSV export.
- Responsive layouts with high-contrast labels and reduced-motion support.
- SQLite database with historical snapshot storage and duplicate-safe ingestion.
- Official Nintendo investor-relations figures for **June 30, 2026** (worldwide, life-to-date unit sales).
- A scheduled checker that compares published reporting dates weekly. **New sales figures are never auto-published without validation.**
- Automated tests and a GitHub Actions quality workflow.

## Quick start

Run in a Python 3.12 environment:

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
streamlit run app.py
~~~

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## Official data sources

- Nintendo [hardware and software unit sales](https://www.nintendo.co.jp/ir/en/finance/hard_soft/index.html)
- Nintendo [Switch 2 best-selling titles](https://www.nintendo.co.jp/ir/en/finance/software/index.html)
- Nintendo [original Switch best-selling titles](https://www.nintendo.co.jp/ir/en/finance/software/switch.html)

**Important definitions:** Reported figures are Nintendo's consolidated, worldwide, life-to-date unit sales as of the stated date. They are not live point-of-sale transactions. Selected leading titles are not a complete genre-level sales census. Some titles include bundled/downloadable copies, Switch 2 Edition reporting can differ, and Pokémon Pokopia excludes Japan under Nintendo's publishing scope. Genre labels are assigned by this project for illustration.

## Update checks

~~~bash
python -m src.refresh
~~~

The script checks Nintendo's current reporting dates. When a new report appears, a new, verified snapshot must be added by a human. The checker does not silently scrape numbers or invent missing values.

## Architecture

Official investor data → verified JSON snapshot → Python ingestion → SQLite → Streamlit/Plotly dashboard

## Roadmap

1. Additional validated quarterly snapshots and regional reporting where disclosed.
2. Normalized title/genre dimensions and more comprehensive data quality checks.
3. Tableau visualization for business intelligence portfolio.
4. Backtested time-series forecasts after enough observations exist.
5. Optional production deployment and API.

## Project integrity

Educational analysis only. No Nintendo logos, cover art, private datasets, or API keys are included. The repository is not affiliated with Nintendo. Please respect official website access rules and update frequency.
