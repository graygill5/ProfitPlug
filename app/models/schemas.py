from pydantic import BaseModel
from typing import Optional, List

class Holding(BaseModel):
    symbol: str
    shares: float
    price: float

class Portfolio(BaseModel):
    title: str
    holdings: List[Holding]

class InfoPage(BaseModel):
    title: str
    content: str

class Updates(BaseModel):
    title: str
    updates: List[str]
