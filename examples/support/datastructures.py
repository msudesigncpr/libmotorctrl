from dataclasses import dataclass


@dataclass
class Colony:
    dish: str
    x: float
    y: float


@dataclass
class PetriDish:
    id: int
    x: int
    y: int


@dataclass
class Well:
    id: str
    x: float
    y: float
    has_sample: bool
    origin: str
