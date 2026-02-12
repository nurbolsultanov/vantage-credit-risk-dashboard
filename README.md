# Vantage Credit Partners — Credit Risk Dashboard

## Project Overview

Portfolio-level credit risk analysis for **Vantage Credit Partners**, a mid-size U.S. consumer lending firm. In Q3 2024, the risk team flagged rising delinquency rates across the personal loan portfolio. This project diagnoses which segments are driving default concentration, quantifies at-risk exposure, and surfaces early warning signals in recent vintages.

**Data scope:** 5,000 loans | 4,500 borrowers | Jan 2021 – Sep 2024 | $91.7M originated

## Live Dashboard

[**→ View on Tableau Public**](https://public.tableau.com/app/profile/nurbol.sultanov/viz/VantageCreditPartnersCreditRiskDashboard/Dashboard1)

## Key Findings

- Portfolio default rate: **15.1%** — Grade F loans default at 30.3% vs Grade A at 1.2%
- **Debt Consolidation & Vacation** loans carry the highest default risk (18%+)
- Borrowers earning **under $35K** default at 2x the rate of those earning over $120K
- **Renters default at 18.6%** vs homeowners at 10.6%
- **Q3 2024 vintage stress signal** — 20.2% default rate, highest of any quarter
- Borrowers aged **21–25** show the highest default rate at 18.3%

## Stack

- **Python** (pandas, NumPy)
- **SQL** (SQLite)
- **Tableau Public** (interactive dashboard)

## Repository Structure

├── data/
│   ├── raw/           # borrowers, loans, loan_status
│   ├── processed/     # 9 aggregated CSVs for Tableau
│   └── sql/           # analysis queries
├── notebooks/
│   └── analysis.py    # full analysis pipeline
└── src/
└── generate_data.py

## Author

Nurbol Sultanov — Data Analyst
[LinkedIn](https://www.linkedin.com/in/nurbolsultanov/) · [GitHub](https://github.com/nurbolsultanov)