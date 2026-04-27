-- =============================================================
-- fact_indicators — WorldBank (annual)
-- =============================================================

INSERT INTO fact_indicators (country_id, indicator_id, time_id, value)
SELECT
    c.country_id,
    i.indicator_id,
    t.time_id,
    s.value
FROM stg_worldbank_raw s
JOIN dim_country   c ON c.country_code   = s.country_code
JOIN dim_indicator i ON i.indicator_code = s.indicator_code
JOIN dim_time      t ON t.year           = s.year
                    AND t.period_type    = 'annual'
WHERE s.value IS NOT NULL
ON CONFLICT (country_id, indicator_id, time_id) DO NOTHING;

-- =============================================================
-- fact_indicators — INSEE IPC (monthly)
-- =============================================================

INSERT INTO fact_indicators (country_id, indicator_id, time_id, value)
SELECT
    c.country_id,
    i.indicator_id,
    t.time_id,
    s.value
FROM stg_insee_raw s
JOIN dim_country   c ON c.country_code   = 'FRA'
JOIN dim_indicator i ON i.indicator_code = s.series
JOIN dim_time      t ON t.year           = CAST(SPLIT_PART(s.period, '-', 1) AS INTEGER)
                    AND t.month          = CAST(SPLIT_PART(s.period, '-', 2) AS INTEGER)
                    AND t.period_type    = 'monthly'
WHERE s.series = 'ipc_france'
  AND s.value IS NOT NULL
ON CONFLICT (country_id, indicator_id, time_id) DO NOTHING;

-- =============================================================
-- fact_indicators — INSEE unemployment (quarterly)
-- =============================================================

INSERT INTO fact_indicators (country_id, indicator_id, time_id, value)
SELECT
    c.country_id,
    i.indicator_id,
    t.time_id,
    s.value
FROM stg_insee_raw s
JOIN dim_country   c ON c.country_code   = 'FRA'
JOIN dim_indicator i ON i.indicator_code = s.series
JOIN dim_time      t ON t.year           = CAST(SPLIT_PART(s.period, '-', 1) AS INTEGER)
                    AND t.quarter        = CAST(SUBSTRING(SPLIT_PART(s.period, '-', 2) FROM 2) AS INTEGER)
                    AND t.period_type    = 'quarterly'
WHERE s.series = 'unemployment_france'
  AND s.value IS NOT NULL
ON CONFLICT (country_id, indicator_id, time_id) DO NOTHING;