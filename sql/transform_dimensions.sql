-- =============================================================
-- Reset dimensions and facts (idempotent: truncate then reload)
-- =============================================================

TRUNCATE TABLE fact_indicators, dim_country, dim_indicator, dim_time
    RESTART IDENTITY CASCADE;

-- =============================================================
-- dim_country
-- =============================================================

INSERT INTO dim_country (country_code, country_name) VALUES
    ('FRA', 'France'),
    ('DEU', 'Germany'),
    ('ESP', 'Spain'),
    ('EUU', 'European Union');

-- =============================================================
-- dim_indicator
-- =============================================================

-- WorldBank indicators (distinct codes + names from staging)
INSERT INTO dim_indicator (indicator_code, indicator_name, unit, source)
SELECT DISTINCT
    indicator_code,
    indicator_name,
    CASE indicator_code
        WHEN 'NY.GDP.MKTP.CD'    THEN 'current USD'
        WHEN 'FP.CPI.TOTL.ZG'   THEN '%'
        WHEN 'SL.UEM.TOTL.ZS'   THEN '%'
        WHEN 'GC.DOD.TOTL.GD.ZS' THEN '% of GDP'
    END,
    'worldbank'
FROM stg_worldbank_raw;

-- INSEE indicators
INSERT INTO dim_indicator (indicator_code, indicator_name, unit, source) VALUES
    ('ipc_france',          'Consumer Price Index - France (Base 2015)', 'index', 'insee'),
    ('unemployment_france', 'Unemployment Rate BIT - Metropolitan France', '%',   'insee');

-- dim_time — annual (WorldBank)
INSERT INTO dim_time (year, month, quarter, period_type)
SELECT DISTINCT year, NULL::INTEGER, NULL::INTEGER, 'annual'
FROM stg_worldbank_raw;

-- dim_time — monthly (INSEE IPC)
INSERT INTO dim_time (year, month, quarter, period_type)
SELECT DISTINCT
    CAST(SPLIT_PART(period, '-', 1) AS INTEGER),
    CAST(SPLIT_PART(period, '-', 2) AS INTEGER),
    NULL::INTEGER,
    'monthly'
FROM stg_insee_raw
WHERE period ~ '^\d{4}-\d{2}$'
  AND series = 'ipc_france';

-- dim_time — quarterly (INSEE unemployment)
INSERT INTO dim_time (year, month, quarter, period_type)
SELECT DISTINCT
    CAST(SPLIT_PART(period, '-', 1) AS INTEGER),
    NULL::INTEGER,
    CAST(SUBSTRING(SPLIT_PART(period, '-', 2) FROM 2) AS INTEGER),
    'quarterly'
FROM stg_insee_raw
WHERE period ~ '^\d{4}-T\d$'
  AND series = 'unemployment_france';