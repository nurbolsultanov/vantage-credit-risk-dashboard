import pandas as pd
import numpy as np
from datetime import date, timedelta
import random

np.random.seed(42)
random.seed(42)

N_BORROWERS = 4500
N_LOANS = 5000

states = ['CA','TX','FL','NY','IL','PA','OH','GA','NC','MI','NJ','VA','WA','AZ','TN',
          'MA','IN','MO','MD','WI','CO','MN','SC','AL','LA','KY','OR','OK','CT','UT']
_sw = [0.12,0.10,0.08,0.08,0.05,0.04,0.04,0.04,0.04,0.03,0.03,0.03,0.03,
       0.03,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.01,0.01,0.01,
       0.01,0.01,0.01,0.01]
state_weights = [x/sum(_sw) for x in _sw]

ages = np.clip(np.random.normal(42, 12, N_BORROWERS).astype(int), 21, 75)
incomes = np.clip(np.random.lognormal(10.8, 0.55, N_BORROWERS).astype(int), 18000, 320000)
emp_lengths = np.random.choice(range(11), N_BORROWERS,
              p=[0.06,0.08,0.09,0.10,0.10,0.10,0.09,0.09,0.09,0.10,0.10])
base_score = 630 + (incomes / 320000) * 180
credit_scores = np.clip((base_score + np.random.normal(0,40,N_BORROWERS)).astype(int), 540, 850)

home_own = []
for inc in incomes:
    if inc < 40000:   home_own.append(np.random.choice(['RENT','OWN','MORTGAGE'], p=[0.60,0.08,0.32]))
    elif inc < 70000: home_own.append(np.random.choice(['RENT','OWN','MORTGAGE'], p=[0.40,0.12,0.48]))
    elif inc < 120000:home_own.append(np.random.choice(['RENT','OWN','MORTGAGE'], p=[0.25,0.15,0.60]))
    else:             home_own.append(np.random.choice(['RENT','OWN','MORTGAGE'], p=[0.12,0.20,0.68]))

borrowers = pd.DataFrame({
    'customer_id': [f'B{str(i).zfill(5)}' for i in range(1, N_BORROWERS+1)],
    'age': ages, 'annual_income': incomes,
    'employment_length_yrs': emp_lengths, 'home_ownership': home_own,
    'state': np.random.choice(states, N_BORROWERS, p=state_weights),
    'credit_score': credit_scores
})
borrowers.to_csv('data/raw/borrowers.csv', index=False)

purposes = ['Debt Consolidation','Home Improvement','Personal','Auto','Medical','Business','Vacation']
pw = [0.35,0.18,0.20,0.10,0.08,0.06,0.03]
start_date = date(2021,1,1)
delta_days = (date(2024,9,30) - start_date).days
loan_ids = [f'L{str(i).zfill(5)}' for i in range(1, N_LOANS+1)]
cust_ids = np.random.choice(borrowers['customer_id'].values, N_LOANS)
orig_dates = [start_date + timedelta(days=random.randint(0, delta_days)) for _ in range(N_LOANS)]
terms = np.random.choice([24,36,48,60], N_LOANS, p=[0.10,0.45,0.25,0.20])

loan_amounts = []
for cid in cust_ids:
    inc = borrowers.loc[borrowers['customer_id']==cid, 'annual_income'].values[0]
    base = min(inc*0.35, 35000)
    loan_amounts.append(int(np.clip(np.random.normal(base,base*0.3),1000,40000)/100)*100)

grades, interest_rates = [], []
for cid in cust_ids:
    cs = borrowers.loc[borrowers['customer_id']==cid,'credit_score'].values[0]
    if cs>=760:   g=np.random.choice(['A','B'],p=[0.75,0.25])
    elif cs>=720: g=np.random.choice(['A','B','C'],p=[0.30,0.50,0.20])
    elif cs>=680: g=np.random.choice(['B','C','D'],p=[0.25,0.50,0.25])
    elif cs>=640: g=np.random.choice(['C','D','E'],p=[0.20,0.50,0.30])
    elif cs>=600: g=np.random.choice(['D','E','F'],p=[0.20,0.45,0.35])
    else:         g=np.random.choice(['E','F'],p=[0.40,0.60])
    grades.append(g)
    interest_rates.append(round({'A':7.5,'B':10.5,'C':13.5,'D':17.0,'E':21.5,'F':26.5}[g]+np.random.normal(0,0.8),2))

loans = pd.DataFrame({
    'loan_id': loan_ids, 'customer_id': cust_ids,
    'origination_date': orig_dates, 'loan_amount': loan_amounts,
    'term_months': terms, 'interest_rate': interest_rates,
    'loan_grade': grades, 'purpose': np.random.choice(purposes, N_LOANS, p=pw)
})
loans.to_csv('data/raw/loans.csv', index=False)

bix = borrowers.set_index('customer_id')
def dp(cid,grade,purpose,od):
    b=bix.loc[cid]; base={'A':0.022,'B':0.055,'C':0.098,'D':0.162,'E':0.235,'F':0.342}[grade]
    inc=b['annual_income']
    if inc<35000: base*=1.55
    elif inc<55000: base*=1.20
    elif inc>100000: base*=0.70
    if b['home_ownership']=='RENT': base*=1.32
    elif b['home_ownership']=='OWN': base*=0.82
    if b['age']<26: base*=1.25
    elif b['age']>65: base*=1.18
    if purpose=='Debt Consolidation': base*=1.22
    elif purpose=='Vacation': base*=1.30
    elif purpose=='Home Improvement': base*=0.85
    if od.year==2024 and od.month>=7: base*=1.45
    elif od.year==2024: base*=1.20
    return min(base,0.85)

statuses,last_pmts,rem_bals,pmts_made=[],[],[],[]
today=date(2024,12,31)
for _,row in loans.iterrows():
    od=row['origination_date']
    if isinstance(od,str): od=date.fromisoformat(od)
    me=min(max((today.year-od.year)*12+(today.month-od.month),1),row['term_months'])
    p=dp(row['customer_id'],row['loan_grade'],row['purpose'],od); r=np.random.random()
    if me>=row['term_months']:
        if r<p*0.6: s='Charged Off';rem=row['loan_amount']*np.random.uniform(0.05,0.45);pm=int(me*np.random.uniform(0.3,0.8))
        else: s='Fully Paid';rem=0;pm=row['term_months']
    elif r<p*0.50: s='Default';rem=row['loan_amount']*np.random.uniform(0.20,0.70);pm=int(me*np.random.uniform(0.1,0.6))
    elif r<p*0.70: s='Late (90+ days)';rem=row['loan_amount']*np.random.uniform(0.30,0.80);pm=int(me*np.random.uniform(0.5,0.85))
    elif r<p*0.85: s='Late (60-89 days)';rem=row['loan_amount']*np.random.uniform(0.40,0.85);pm=int(me*np.random.uniform(0.6,0.90))
    elif r<p*0.95: s='Late (30-59 days)';rem=row['loan_amount']*np.random.uniform(0.50,0.90);pm=int(me*np.random.uniform(0.7,0.95))
    else: s='Current';rem=row['loan_amount']*max(0,1-me/row['term_months']);pm=me
    statuses.append(s);rem_bals.append(round(rem,2));pmts_made.append(pm)
    last_pmts.append(today-timedelta(days=random.randint(0,35) if s=='Current' else random.randint(30,180)))

pd.DataFrame({'loan_id':loan_ids,'status':statuses,'last_payment_date':last_pmts,
              'remaining_balance':rem_bals,'payments_made':pmts_made}
).to_csv('data/raw/loan_status.csv',index=False)
print("Done."); print(pd.Series(statuses).value_counts())