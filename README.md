\# 📈 Nifty100 Financial Analytics Platform



A production-ready \*\*financial analytics and stock intelligence platform\*\* built using Python, SQLite, Streamlit, and data engineering best practices.



The platform analyzes Nifty100 companies using financial statements, market data, financial ratios, peer benchmarking, screening algorithms, and interactive dashboards.



Built as a complete fintech analytics project covering:



\- Data Engineering

\- Financial Analytics

\- Quantitative Metrics

\- Stock Screening

\- Peer Comparison

\- Interactive Visualization

\- Dashboard Development





\---



\# 🚀 Project Overview



The Nifty100 Financial Analytics Platform transforms raw financial datasets into meaningful investment insights.



The system performs:





\---



\# ✨ Features



\## ✅ Sprint 1 — Data Foundation (Completed)



\### ETL Pipeline



Implemented a complete data ingestion and validation pipeline.



Features:



\- Excel/CSV data loading

\- Data cleaning

\- Schema validation

\- SQLite database creation

\- Data quality checks





Database tables:



\---



\# ✅ Sprint 2 — Financial Analytics Engine (Completed)



The analytics engine calculates 50+ financial KPIs.



Implemented metrics:



\## Profitability



\- Net Profit Margin

\- Operating Profit Margin

\- Return on Equity (ROE)

\- Return on Capital Employed (ROCE)

\- Return on Assets (ROA)





\## Leverage



\- Debt to Equity Ratio

\- Interest Coverage Ratio

\- Debt Free Detection





\## Efficiency



\- Asset Turnover





\## Cash Flow



\- Free Cash Flow

\- Capex Intensity

\- FCF Conversion





\## Growth



\- Revenue CAGR (5 Years)

\- PAT CAGR (5 Years)

\- EPS CAGR (5 Years)





\## Quality Score



Composite financial quality scoring system.



\---



\# ✅ Sprint 3 — Screener \& Peer Intelligence (Completed)



\## Financial Screener



Supports:



\- Quality Compounder

\- Value Pick

\- Growth Accelerator

\- Dividend Champion

\- Debt Free Bluechip

\- Turnaround Watch





Custom filters:



\- ROE

\- ROCE

\- Net Margin

\- OPM

\- Debt/Equity

\- Interest Coverage

\- Free Cash Flow

\- CAGR Growth

\- Market Cap

\- PE Ratio

\- PB Ratio

\- Dividend Yield





\---



\## Peer Analysis Engine



Implemented peer benchmarking using:



\- Sector groups

\- Peer clusters

\- Percentile ranking





Metrics:



\- ROE percentile

\- ROCE percentile

\- Profitability percentile

\- Growth percentile

\- Quality percentile





\---



\# ✅ Sprint 4 — Financial Intelligence Dashboard (Completed)



Interactive Streamlit dashboard.



\## Dashboard Modules



\### 🏠 Market Overview



Displays:



\- Company universe

\- Financial records

\- Peer rankings

\- Market data statistics

\- Sector distribution





\---



\### 🏢 Company Profile



Provides:



\- Company information

\- Financial ratios

\- Historical performance

\- Stock price movement

\- Radar comparison





\---



\### 🔍 Financial Screener



Interactive screening interface connected with Sprint 3 engine.





\---



\### 👥 Peer Analysis



Displays:



\- Peer comparison

\- Percentile rankings

\- Relative performance





\---



\### 📈 Financial Trends



Visualizes:



\- Revenue trends

\- Profit trends

\- Margin changes

\- Growth analysis





\---



\### 🏭 Sector Analysis



Analyzes:



\- Sector distribution

\- Market capitalization

\- Industry performance





\---



\### 💰 Capital Analysis



Tracks:



\- ROE trends

\- ROCE trends

\- Capital efficiency





\---



\### 📄 Reports



Provides:



\- Exportable analysis

\- Screening reports

\- Financial summaries





\---



\# ✅ Sprint 7 — Automated Report Generation (Completed)



Static report generation for the Nifty100 universe, powered by the database and the earlier sprint engines.



\## Report Modules



\### 📄 Company Tearsheets



One-page PNG tearsheet per company:



\- Company header (name, sector, industry, market-cap category, Sprint 6 cluster)

\- Key metrics strip (ROE, ROCE, OPM, NPM, D/E, quality, market cap, P/E)

\- Revenue & profit, return metrics and cash-flow trend charts

\- Latest 8 years of financial history table

\- Sprint 5 pros & cons summary





\### 🏭 Sector Reports



One-page PNG report per sector:



\- Average sector metrics (ROE, ROCE, margins, D/E, quality)

\- Company quality ranking bar chart

\- Top companies table by quality score





\### 📊 Portfolio Summary



Full-universe summary:



\- Average market metrics strip

\- Quality and market-cap charts by sector

\- Top-10 companies by quality table

\- output/portfolio_summary.csv (one row per company, enriched with Sprint 6 cluster labels)





\## Generated Outputs



\- reports/tearsheets/<COMPANY_ID>_tearsheet.png (92 files)

\- reports/sectors/<sector>_report.png (10 files)

\- reports/portfolio_summary.png

\- output/portfolio_summary.csv





\## Run Commands



\- python -m src.reports.tearsheet

\- python -m src.reports.sector_report

\- python -m src.reports.portfolio_summary





\---



\# 🏗️ Project Architecture



\---



\# 🛠️ Technology Stack



\## Programming



\- Python 3.13





\## Data Engineering



\- Pandas

\- NumPy

\- SQLite





\## Analytics



\- Financial Ratio Modeling

\- CAGR Calculations

\- Quantitative Scoring





\## Visualization



\- Plotly

\- Matplotlib





\## Dashboard



\- Streamlit





\## Database



\- SQLite





\---



\# ⚙️ Installation



Clone repository:



```bash

git clone https://github.com/varan25bce11150-tech/nifty100-project.git



cd nifty100-project

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

streamlit run src/dashboard/app.py

pytest

Sprint 1  ✅ Complete

Sprint 2  ✅ Complete

Sprint 3  ✅ Complete

Sprint 4  ✅ Complete

Sprint 5  ✅ Complete

Sprint 6  ✅ Complete

Sprint 7  ✅ Complete

