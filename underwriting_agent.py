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