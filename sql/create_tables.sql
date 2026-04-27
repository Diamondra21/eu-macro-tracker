-- =============================================================
-- Staging tables: raw data as received from APIs
-- =============================================================

CREATE TABLE IF NOT EXISTS stg_worldbank_raw (
    id             SERIAL PRIMARY KEY,
    country_code   VARCHAR(10)     NOT NULL,
    indicator_code VARCHAR(50)     NOT NULL,
    indicator_name VARCHAR(200),
    year           INTEGER         NOT NULL,
    value          NUMERIC(20, 4),
    loaded_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (country_code, indicator_code, year)
);

CREATE TABLE IF NOT EXISTS stg_insee_raw (
    id        SERIAL PRIMARY KEY,
    id_bank   VARCHAR(20)     NOT NULL,
    series    VARCHAR(100)    NOT NULL,
    period    VARCHAR(10)     NOT NULL,  -- format: YYYY-MM
    value     NUMERIC(20, 4),
    loaded_at TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (id_bank, period)
);

-- =============================================================
-- Dimension tables
-- =============================================================

CREATE TABLE IF NOT EXISTS dim_country (
    country_id   SERIAL PRIMARY KEY,
    country_code VARCHAR(10)  NOT NULL UNIQUE,
    country_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_indicator (
    indicator_id   SERIAL PRIMARY KEY,
    indicator_code VARCHAR(50)  NOT NULL UNIQUE,
    indicator_name VARCHAR(200) NOT NULL,
    unit           VARCHAR(50),
    source         VARCHAR(20)  NOT NULL  -- 'worldbank' | 'insee'
);

CREATE TABLE IF NOT EXISTS dim_time (
    time_id     SERIAL PRIMARY KEY,
    year        INTEGER      NOT NULL,
    month       INTEGER,                  -- NULL for annual data
    quarter     INTEGER,                  -- NULL for annual data
    period_type VARCHAR(10)  NOT NULL,    -- 'annual' | 'monthly' | 'quarterly'
    UNIQUE (year, month, period_type)
);

-- =============================================================
-- Fact table
-- =============================================================

CREATE TABLE IF NOT EXISTS fact_indicators (
    fact_id      SERIAL PRIMARY KEY,
    country_id   INTEGER      NOT NULL REFERENCES dim_country(country_id),
    indicator_id INTEGER      NOT NULL REFERENCES dim_indicator(indicator_id),
    time_id      INTEGER      NOT NULL REFERENCES dim_time(time_id),
    value        NUMERIC(20, 4),
    loaded_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (country_id, indicator_id, time_id)
);