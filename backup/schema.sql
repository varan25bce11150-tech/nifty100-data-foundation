PRAGMA foreign_keys = ON;

-- ===========================================
-- Companies
-- ===========================================
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL,
    ticker TEXT UNIQUE,
    isin TEXT,
    website TEXT,
    sector_id INTEGER
);

-- ===========================================
-- Sectors
-- ===========================================
CREATE TABLE IF NOT EXISTS sectors (
    sector_id INTEGER PRIMARY KEY,
    sector_name TEXT NOT NULL
);

-- ===========================================
-- Profit & Loss
-- ===========================================
CREATE TABLE IF NOT EXISTS profitandloss (
    company_id INTEGER,
    year INTEGER,
    sales REAL,
    expenses REAL,
    operating_profit REAL,
    net_profit REAL,
    opm_percentage REAL,
    eps REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- Balance Sheet
-- ===========================================
CREATE TABLE IF NOT EXISTS balancesheet (
    company_id INTEGER,
    year INTEGER,
    total_assets REAL,
    total_liabilities REAL,
    equity REAL,
    reserves REAL,
    debt REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- Cash Flow
-- ===========================================
CREATE TABLE IF NOT EXISTS cashflow (
    company_id INTEGER,
    year INTEGER,
    operating_activity REAL,
    investing_activity REAL,
    financing_activity REAL,
    net_cash_flow REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- Analysis
-- ===========================================
CREATE TABLE IF NOT EXISTS analysis (
    company_id INTEGER,
    year INTEGER,
    remark TEXT,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- Documents
-- ===========================================
CREATE TABLE IF NOT EXISTS documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    document_name TEXT,
    document_url TEXT,
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- Pros and Cons
-- ===========================================
CREATE TABLE IF NOT EXISTS prosandcons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    type TEXT,
    description TEXT,
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- Stock Prices
-- ===========================================
CREATE TABLE IF NOT EXISTS stock_prices (
    company_id INTEGER,
    trade_date DATE,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER,
    PRIMARY KEY(company_id, trade_date),
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- Financial Ratios
-- ===========================================
CREATE TABLE IF NOT EXISTS financial_ratios (
    company_id INTEGER,
    year INTEGER,
    roe REAL,
    roce REAL,
    pe REAL,
    pb REAL,
    debt_equity REAL,
    current_ratio REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
);

-- ===========================================
-- Peer Groups
-- ===========================================
CREATE TABLE IF NOT EXISTS peer_groups (
    company_id INTEGER,
    peer_company_id INTEGER,
    PRIMARY KEY(company_id, peer_company_id)
);

-- ===========================================
-- Market Cap
-- ===========================================
CREATE TABLE IF NOT EXISTS market_cap (
    company_id INTEGER,
    year INTEGER,
    market_cap REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
);