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

