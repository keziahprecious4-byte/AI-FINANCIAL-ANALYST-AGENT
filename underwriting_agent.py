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