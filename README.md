# eu-macro-tracker

Automated ELT pipeline for European macroeconomic indicators.

## Business question
How do inflation, unemployment, and growth in France evolve,
and how do they compare to other European countries?

## Architecture
ELT approach: Python extracts and loads raw data into PostgreSQL staging tables,
SQL transforms into a star schema for analysis.

## Indicators
| Indicator | Source | Countries |
|---|---|---|
| Inflation (CPI) | INSEE API | France |
| Unemployment | INSEE API | France |
| GDP | World Bank API | FR, DE, ES, EU |
| Public debt (% GDP) | World Bank API | FR, DE, ES, EU |

## Tech stack
Python 3.11.9 · PostgreSQL 16 (Docker) · Git/GitHub · pytest

## Status
🚧 In development