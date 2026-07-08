PRAGMA foreign_keys = ON;


CREATE TABLE IF NOT EXISTS companies (

    id TEXT PRIMARY KEY,
    company_logo TEXT,
    company_name TEXT,
    chart_link TEXT,
    about_company TEXT,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    face_value REAL,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL
);



CREATE TABLE IF NOT EXISTS profitandloss (

    id INTEGER PRIMARY KEY,
    company_id TEXT,
    year INTEGER,
    sales REAL,
    expenses REAL,
    operating_profit REAL,
    opm_percentage REAL,
    other_income REAL,
    interest REAL,
    depreciation REAL,
    profit_before_tax REAL,
    tax_percentage REAL,
    net_profit REAL,
    eps REAL,
    dividend_payout REAL,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
);



CREATE TABLE IF NOT EXISTS balancesheet (

    id INTEGER PRIMARY KEY,
    company_id TEXT,
    year INTEGER,
    equity_capital REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL,
    fixed_assets REAL,
    cwip REAL,
    investments REAL,
    other_asset REAL,
    total_assets REAL,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
);



CREATE TABLE IF NOT EXISTS cashflow (

    id INTEGER PRIMARY KEY,
    company_id TEXT,
    year INTEGER,
    operating_activity REAL,
    investing_activity REAL,
    financing_activity REAL,
    net_cash_flow REAL,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
);



CREATE TABLE IF NOT EXISTS stock_prices (

    id INTEGER PRIMARY KEY,
    company_id TEXT,
    date TEXT,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER,
    adjusted_close REAL
);



CREATE TABLE IF NOT EXISTS analysis (

    id INTEGER PRIMARY KEY,
    company_id TEXT,
    compounded_sales_growth REAL,
    compounded_profit_growth REAL,
    stock_price_cagr REAL,
    roe REAL
);



CREATE TABLE IF NOT EXISTS documents (

    id INTEGER PRIMARY KEY,
    company_id TEXT,
    Year INTEGER,
    Annual_Report TEXT
);



CREATE TABLE IF NOT EXISTS prosandcons (

    id INTEGER PRIMARY KEY,
    company_id TEXT,
    pros TEXT,
    cons TEXT
);



CREATE TABLE IF NOT EXISTS sectors (

    id INTEGER PRIMARY KEY,
    company_id TEXT,
    sector TEXT,
    industry TEXT,
    ratio REAL,
    market_cap_category TEXT
);



CREATE TABLE IF NOT EXISTS financial_ratios (

    id INTEGER PRIMARY KEY,
    company_id TEXT,
    period TEXT,
    ratio1 REAL,
    ratio2 REAL,
    ratio3 REAL,
    ratio4 REAL,
    ratio5 REAL,
    ratio6 REAL,
    ratio7 REAL,
    ratio8 REAL,
    ratio9 REAL,
    ratio10 REAL,
    ratio11 REAL,
    ratio12 REAL,
    ratio13 REAL
);



CREATE TABLE IF NOT EXISTS peer_groups (

    id INTEGER PRIMARY KEY,
    sector TEXT,
    company TEXT,
    is_peer TEXT
);



CREATE TABLE IF NOT EXISTS market_cap (

    id INTEGER PRIMARY KEY,
    company_id TEXT,
    year INTEGER,
    market_cap REAL,
    enterprise_value REAL,
    pe_ratio REAL,
    pb_ratio REAL,
    dividend_yield REAL,
    other_ratio REAL

);