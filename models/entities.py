from dataclasses import dataclass

@dataclass
class Vehicle:
    plate: str
    vehicle_type: str
    brand: str = ""
    color: str = ""
    owner: str = ""

@dataclass
class Coupon:
    code: str
    discount: int

@dataclass
class Payment:
    session_id: int
    amount: float
    method: str
    discount: float = 0
