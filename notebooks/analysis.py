import pandas as pd
import numpy as np

BASE = '.'
loans     = pd.read_csv(f'{BASE}/data/raw/loans.csv', parse_dates=['origination_date'])
borrowers = pd.read_csv(f'{BASE}/data/raw/borrowers.csv')
status    = pd.read_csv(f'{BASE}/data/raw/loan_status.csv')

df = loans.merge(status, on='loan_id').merge(borrowers, on='customer_id')
df['is_default']   = df['status'].isin(['Default','Charged Off']).astype(int)
df['is_delinquent']= df['status'].str.startswith('Late').astype(int)
df['orig_year']    = df['origination_date'].dt.year
df['orig_quarter'] = df['origination_date'].dt.quarter
df['orig_yrq']     = df['orig_year'].astype(str) + '-Q' + df['orig_quarter'].astype(str)

def income_band(i):
    if i<35000: return '1_Under 35K'
    if i<55000: return '2_35K-55K'
    if i<80000: return '3_55K-80K'
    if i<120000:return '4_80K-120K'
    return '5_Over 120K'

def age_band(a):
    if a<26: return '1_21-25'
    if a<35: return '2_26-34'
    if a<45: return '3_35-44'
    if a<55: return '4_45-54'
    if a<65: return '5_55-64'
    return '6_65+'

df['income_band'] = df['annual_income'].apply(income_band)
df['age_band']    = df['age'].apply(age_band)

import os
os.makedirs('data/processed', exist_ok=True)

# 1. master table
df.to_csv('data/processed/master_loan_table.csv', index=False)

# 2. by grade
df.groupby('loan_grade').agg(
    total_loans=('loan_id','count'),
    total_originated=('loan_amount','sum'),
    avg_loan_amount=('loan_amount','mean'),
    avg_interest_rate=('interest_rate','mean'),
    defaults=('is_default','sum'),
    default_rate=('is_default','mean'),
).reset_index().assign(default_rate=lambda x: x['default_rate']*100
).to_csv('data/processed/by_grade.csv', index=False)

# 3. by purpose
df.groupby('purpose').agg(
    total_loans=('loan_id','count'),
    total_originated=('loan_amount','sum'),
    defaults=('is_default','sum'),
    default_rate=('is_default','mean'),
).reset_index().assign(default_rate=lambda x: x['default_rate']*100
).sort_values('default_rate', ascending=False
).to_csv('data/processed/by_purpose.csv', index=False)

# 4. by income band
df.groupby('income_band').agg(
    total_loans=('loan_id','count'),
    default_rate=('is_default','mean'),
    avg_credit_score=('credit_score','mean'),
).reset_index().assign(default_rate=lambda x: x['default_rate']*100
).sort_values('income_band'
).to_csv('data/processed/by_income.csv', index=False)

# 5. by home ownership
df.groupby('home_ownership').agg(
    total_loans=('loan_id','count'),
    default_rate=('is_default','mean'),
    avg_loan_amount=('loan_amount','mean'),
).reset_index().assign(default_rate=lambda x: x['default_rate']*100
).to_csv('data/processed/by_home_ownership.csv', index=False)

# 6. vintage
df.groupby(['orig_year','orig_quarter','orig_yrq']).agg(
    total_loans=('loan_id','count'),
    total_originated=('loan_amount','sum'),
    default_rate=('is_default','mean'),
    delinquency_rate=('is_delinquent','mean'),
).reset_index().assign(
    default_rate=lambda x: x['default_rate']*100,
    delinquency_rate=lambda x: x['delinquency_rate']*100,
).sort_values(['orig_year','orig_quarter']
).to_csv('data/processed/vintage.csv', index=False)

# 7. by state
df.groupby('state').agg(
    total_loans=('loan_id','count'),
    total_originated=('loan_amount','sum'),
    default_rate=('is_default','mean'),
).reset_index().assign(default_rate=lambda x: x['default_rate']*100
).query('total_loans >= 10'
).to_csv('data/processed/by_state.csv', index=False)

# 8. by age band
df.groupby('age_band').agg(
    total_loans=('loan_id','count'),
    default_rate=('is_default','mean'),
    avg_loan_amount=('loan_amount','mean'),
).reset_index().assign(default_rate=lambda x: x['default_rate']*100
).sort_values('age_band'
).to_csv('data/processed/by_age.csv', index=False)

# 9. status distribution
df.groupby('status').agg(
    count=('loan_id','count'),
    total_balance=('remaining_balance','sum'),
).reset_index().assign(pct=lambda x: x['count']/x['count'].sum()*100
).to_csv('data/processed/status_distribution.csv', index=False)

print("All CSVs saved to data/processed/")
print(f"\nPortfolio default rate: {df['is_default'].mean()*100:.1f}%")
print(f"Total originated: ${df['loan_amount'].sum():,.0f}")
print(f"Total loans: {len(df):,}")