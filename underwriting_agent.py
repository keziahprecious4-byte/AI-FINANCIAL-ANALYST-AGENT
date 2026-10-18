import os
from dataclasses import dataclass, field

@dataclass
class Application:
    id: str
    age: int
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

def explain(app, d):
    return f"{d.outcome} by {d.decided_by}. Trail: " + " | ".join(d.trail)

#Agent 
def underwrite(app):
    d = Decision(app.id)

    if not verify_and_open(app, d):
        d.outcome = "DECLINED"
        d.rationale = explain(app, d); return d

    d.fraud = fraud_score(app)
    d.log("fraud", f"score {d.fraud:.2f}")
    if d.fraud >= FRAUD_DECLINE:
        d.outcome = "DECLINED"; d.log("fraud", "above decline threshold")
        d.rationale = explain(app, d); return d
    if d.fraud >= FRAUD_REFER:
        d.outcome, d.decided_by = "ESCALATED", "human (fraud referral)"
        d.log("fraud", "above referral threshold -> human review")
        d.rationale = explain(app, d); return d

    d.risk = risk_score(app)
    d.log("risk", f"score {d.risk:.2f}")
    d.premium, ded = price_and_terms(app, d.risk)
    d.log("price", f"premium EUR {d.premium:,.2f}, deductible EUR {ded}")

    if app.limit > APPETITE[app.product]:
        d.outcome = "DECLINED"
        d.log("appetite", f"limit exceeds {app.product} appetite")
        d.rationale = explain(app, d); return d
    d.log("appetite", "within appetite & capacity")

    if app.limit > AGENT_AUTHORITY_LIMIT or d.risk >= RISK_ESCALATE:
        d.outcome, d.decided_by = "ESCALATED", "human (authority limit)"
        d.log("authority", "outside agent authority -> senior underwriter")
        d.rationale = explain(app, d); return d
    d.log("authority", "within agent authority")

    d.outcome = "BOUND"
    d.log("bind", "policy issued (no human sign-off)")
    d.rationale = explain(app, d)
    return d

#Demo
if __name__ == "__main__":
    samples = [
        Application("A1", 34, "auto", 60_000, 55_000, 0, 740, True),   # clean - bound
        Application("A2", 22, "auto", 80_000, 30_000, 2, 580, True),   # risky - escalate
        Application("A3", 45, "home", 900_000, 90_000, 0, 700, True),  # over authority
        Application("A4", 50, "life", 400_000, 40_000, 1, 690, False), # doc mismatch - fraud
        Application("A5", 16, "auto", 20_000, 10_000, 0, 700, True),   # knockout
        Application("A6", 40, "auto", 900_000, 70_000, 0, 760, True),  # outside appetite
    ]
    results = [underwrite(a) for a in samples]
    for d in results:
        print(f"\n[{d.app_id}] {d.outcome:<9} decided by: {d.decided_by}")
        for line in d.trail:
            print("   -", line)
    auto = sum(d.decided_by == "agent" and d.outcome == "BOUND" for d in results)
    print(f"\nSummary: {len(results)} cases | agent-bound without sign-off: {auto} "
          f"| escalated to humans: {sum(d.outcome == 'ESCALATED' for d in results)}")
