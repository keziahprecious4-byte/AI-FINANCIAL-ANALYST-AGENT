import os
from dataclasses import dataclass, field

@dataclass
class Application:
    id: str
    product: str
    limit: float 
    income: float
    claims_5y: int
    credit_score: int  
    docs_consistent: bool

@dataclass
class Decision:
    app_id: str
    outcome: str = "PENDING"     
    decided_by: str = "agent"
    risk: float = 0.0
    fraud: float = 0.0
    premium: float = 0.0
    trail: list = field(default_factory=list)
    rationale: str = ""

    def log(self, step, detail):
        self.trail.append(f"{step}: {detail}")

#Policy
APPETITE = {"auto": 500_000, "home": 1_500_000, "life": 1_000_000}
AGENT_AUTHORITY_LIMIT = 250_000
FRAUD_REFER = 0.60  #refer to human
FRAUD_DECLINE = 0.85   
RISK_ESCALATE = 0.50 
BASE_RATE = {"auto": 0.012, "home": 0.004, "life": 0.002}

#Tools
def verify_and_open(app, d):
   if app.age < 18 or app.age > 85: 
       d.log("verify", f"knockout: age {app.age} outside 18-85")
       return False
   if app.limit <= 0 or app.income <= 0:
       d.log("verify", "knockout: invalid limit/income")
       return False
   d.log("verify", "eligible, case opened")
   return True

def fraud_score(app):
    s = 0.0
    if not app.docs_consistent:
        s += 0.55
    if app.limit > app.income * 8:
        s += 0.25
    if app.claims_5y >= 3:
        s += 0.20
    return min(s, 1.0) 

def risk_score(app):
    r = 0.15
    r += 0.12 * min(app.claims_5y, 4)
    r += (650 - app.credit_score) / 1000 if app.credit_score < 650 else -0.05
    r += 0.10 if app.age < 25 or app.age > 70 else 0
    return max(0.0, min(r, 1.0))

def price_and_terms(app, risk):
    premium = app.limit * BASE_RATE[app.product] * (1 + 2 * risk)
    deductible = 500 if risk < 0.4 else 1500
    return round(premium, 2), deductible