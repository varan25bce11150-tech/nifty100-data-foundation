# 📈 Nifty100 Financial Analytics Platform

An end-to-end financial analytics platform built with Python, Pandas, SQLite and Streamlit to explore and compare Nifty100 companies using financial data, market metrics and peer analysis.

The project started as a data engineering pipeline and gradually grew into a complete analytics platform with financial ratios, stock screeners, peer benchmarking, interactive dashboards and automated reports.

## What the Project Does

The platform takes raw financial and market data and turns it into useful company-level and sector-level analysis.

It currently covers:

- Data ingestion and validation
- Financial ratio calculations
- Company quality scoring
- Stock screening
- Peer comparison
- Sector analysis
- Market and valuation metrics
- Interactive dashboards
- Automated financial reports


## 📊 Project Scale

- 92 companies analyzed
- 10 sectors
- 50+ financial KPIs
- 6 screening strategies
- 11 peer groups
- 92 company tearsheets
- 10 sector reports
- Portfolio-level summary reports


# ✨ Main Features

## 1. Data Engineering

The project includes a complete data ingestion and validation pipeline for bringing financial datasets into a structured SQLite database.

The pipeline handles:

- Excel and CSV data loading
- Data cleaning
- Schema validation
- Data quality checks
- SQLite database creation
- Financial data transformation

The database stores information such as:

- Company details
- Profit & loss data
- Balance sheets
- Cash flows
- Stock prices
- Financial ratios
- Market capitalization
- Peer groups
- Sector information


## 2. Financial Analytics

The analytics layer calculates more than 50 financial KPIs across profitability, leverage, efficiency, cash flow and growth.

### Profitability

- Net Profit Margin
- Operating Profit Margin
- Return on Equity (ROE)
- Return on Capital Employed (ROCE)
- Return on Assets (ROA)

### Leverage

- Debt to Equity Ratio
- Interest Coverage Ratio
- Debt-free detection

### Efficiency

- Asset Turnover

### Cash Flow

- Free Cash Flow
- Capex Intensity
- FCF Conversion

### Growth

- Revenue CAGR (5 Years)
- PAT CAGR (5 Years)
- EPS CAGR (5 Years)

### Quality Scoring

A composite quality score is used to compare companies across multiple financial metrics.


# 🔍 Stock Screener

The platform includes six predefined screening strategies:

- Quality Compounder
- Value Pick
- Growth Accelerator
- Dividend Champion
- Debt Free Bluechip
- Turnaround Watch

The screener can filter companies using metrics such as:

- ROE
- ROCE
- Net Margin
- Operating Profit Margin
- Debt/Equity
- Interest Coverage
- Free Cash Flow
- Revenue/PAT growth
- Market Capitalization
- P/E Ratio
- P/B Ratio
- Dividend Yield


# 👥 Peer Analysis

Companies can be compared with their sector peers using peer groups and percentile rankings.

The peer analysis engine includes:

- Sector-based peer groups
- Peer clusters
- Percentile rankings
- Relative company comparison

Some of the metrics used for comparison include:

- ROE percentile
- ROCE percentile
- Profitability percentile
- Growth percentile
- Quality percentile


# 📊 Streamlit Dashboard

The project includes an interactive Streamlit dashboard for exploring the financial data and analytics.

### Market Overview

Provides an overview of:

- Company universe
- Financial records
- Peer rankings
- Market data
- Sector distribution

### Company Profile

Provides a detailed view of an individual company, including:

- Company information
- Financial ratios
- Historical performance
- Stock price movement
- Radar comparison

### Financial Screener

Allows users to explore companies using the predefined screening strategies and financial filters.

### Peer Analysis

Shows:

- Peer comparison
- Percentile rankings
- Relative performance

### Financial Trends

Visualizes:

- Revenue trends
- Profit trends
- Margin changes
- Growth patterns

### Sector Analysis

Provides analysis of:

- Sector distribution
- Market capitalization
- Industry performance

### Capital Analysis

Tracks metrics such as:

- ROE trends
- ROCE trends
- Capital efficiency

### Reports

Provides access to financial summaries, screening results and generated reports.


# 📄 Automated Reports

The project also generates static reports from the financial database.

## Company Tearsheets

A one-page report is generated for each company containing:

- Company information
- Sector and industry
- Market-cap category
- Key financial metrics
- Revenue and profit trends
- Return metrics
- Cash-flow trends
- Historical financial data
- Pros and cons summary

92 company tearsheets are currently generated.

## Sector Reports

Each sector receives a one-page report containing:

- Average sector metrics
- ROE and ROCE
- Profitability margins
- Debt/Equity
- Quality metrics
- Company quality rankings
- Top companies by quality score

10 sector reports are currently generated.

## Portfolio Summary

The portfolio-level report provides:

- Overall market metrics
- Quality analysis by sector
- Market-cap analysis
- Top companies by quality score
- Company-level summary data

The generated portfolio summary is also available as:

`output/portfolio_summary.csv`


# 🏗️ Project Architecture

```text
Raw Financial Data
       │
       ▼
Data Ingestion
       │
       ▼
Cleaning & Validation
       │
       ▼
SQLite Database
       │
       ▼
Financial Analytics
       │
       ├───────────────┐
       ▼               ▼
Stock Screener    Peer Analysis
       │               │
       └───────┬───────┘
               ▼
       Streamlit Dashboard
               │
               ▼
       Automated Reports


       🛠️ Technology Stack
Programming
Python 3.13
Data Processing
Pandas
NumPy
Database
SQLite
Financial Analytics
Financial ratio modeling
CAGR calculations
Quantitative scoring
Peer percentile analysis
Visualization
Plotly
Matplotlib
Dashboard
Streamlit
Testing
Pytest
📁 Project Structure

nifty100-data-foundation/
│
├── data/
├── output/
├── reports/
├── tests/
│
├── src/
│   ├── dashboard/
│   ├── analytics/
│   ├── reports/
│   └── ...
│
├── requirements.txt
├── README.md
└── nifty100.db


⚙️ Installation

Clone the repository:

git clone https://github.com/varan25bce11150-tech/nifty100-data-foundation.git

cd nifty100-data-foundation

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

streamlit run src/dashboard/app.py

pytest


csv
📌 Development History

The project was developed incrementally through multiple stages:

Sprint 1 — Data Foundation
Sprint 2 — Financial Analytics
Sprint 3 — Screener & Peer Intelligence
Sprint 4 — Financial Intelligence Dashboard
Sprint 5 — NLP / Pros & Cons Analysis
Sprint 6 — Company Clustering
Sprint 7 — Automated Report Generation

Each stage added another layer to the platform, from the initial data pipeline to the final analytics and reporting workflow.

🚧 Future Improvements

Some areas I would like to explore further:

More real-time market data integration
Additional valuation models
More advanced portfolio analytics
Improved dashboard filtering
Automated data refresh workflows
Cloud deployment
More comprehensive test coverage
👨‍💻 About

This project was built as a hands-on project to understand how financial data can be collected, cleaned, stored and transformed into useful analytics.

The main focus was on building the complete workflow rather than only creating individual financial charts or models.
