from dataclasses import dataclass

STERILIZER_COORDINATES = (461_330, 87_950, 60_000)  # Micrometers  # TODO
PETRI_DISH_DEPTH = 80_000  # Micrometers # TODO Check depth
WELL_DEPTH = 80_000  # Micrometers # TODO Check depth
CAMERA_POS_OFFSET = 20  # Micrometers # TODO Find real value


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


PETRI_DISHS = [
    PetriDish(id=1, x=2600, y=-2460),
    PetriDish(id=2, x=7100, y=-2460),
    PetriDish(id=3, x=11600, y=-2460),
    PetriDish(id=4, x=16100, y=-2460),
    PetriDish(id=5, x=2600, y=2290),
    PetriDish(id=6, x=7100, y=2290),
]

WELLS = [
    Well(id="A1", x=267.79, y=31.08, has_sample=False, origin=None),
    Well(id="A2", x=276.86, y=31.08, has_sample=False, origin=None),
    Well(id="A3", x=285.93, y=31.08, has_sample=False, origin=None),
    Well(id="A4", x=295.00, y=31.08, has_sample=False, origin=None),
    Well(id="A5", x=304.07, y=31.08, has_sample=False, origin=None),
    Well(id="A6", x=313.14, y=31.08, has_sample=False, origin=None),
    Well(id="A7", x=322.21, y=31.08, has_sample=False, origin=None),
    Well(id="A8", x=331.28, y=31.08, has_sample=False, origin=None),
    Well(id="A9", x=340.35, y=31.08, has_sample=False, origin=None),
    Well(id="A10", x=349.42, y=31.08, has_sample=False, origin=None),
    Well(id="A11", x=358.49, y=31.08, has_sample=False, origin=None),
    Well(id="A12", x=367.56, y=31.08, has_sample=False, origin=None),
    Well(id="B1", x=267.79, y=40.15, has_sample=False, origin=None),
    Well(id="B2", x=276.86, y=40.15, has_sample=False, origin=None),
    Well(id="B3", x=285.93, y=40.15, has_sample=False, origin=None),
    Well(id="B4", x=295.00, y=40.15, has_sample=False, origin=None),
    Well(id="B5", x=304.07, y=40.15, has_sample=False, origin=None),
    Well(id="B6", x=313.14, y=40.15, has_sample=False, origin=None),
    Well(id="B7", x=322.21, y=40.15, has_sample=False, origin=None),
    Well(id="B8", x=331.28, y=40.15, has_sample=False, origin=None),
    Well(id="B9", x=340.35, y=40.15, has_sample=False, origin=None),
    Well(id="B10", x=349.42, y=40.15, has_sample=False, origin=None),
    Well(id="B11", x=358.49, y=40.15, has_sample=False, origin=None),
    Well(id="B12", x=367.56, y=40.15, has_sample=False, origin=None),
    Well(id="C1", x=267.79, y=49.22, has_sample=False, origin=None),
    Well(id="C2", x=276.86, y=49.22, has_sample=False, origin=None),
    Well(id="C3", x=285.93, y=49.22, has_sample=False, origin=None),
    Well(id="C4", x=295.00, y=49.22, has_sample=False, origin=None),
    Well(id="C5", x=304.07, y=49.22, has_sample=False, origin=None),
    Well(id="C6", x=313.14, y=49.22, has_sample=False, origin=None),
    Well(id="C7", x=322.21, y=49.22, has_sample=False, origin=None),
    Well(id="C8", x=331.28, y=49.22, has_sample=False, origin=None),
    Well(id="C9", x=340.35, y=49.22, has_sample=False, origin=None),
    Well(id="C10", x=349.42, y=49.22, has_sample=False, origin=None),
    Well(id="C11", x=358.49, y=49.22, has_sample=False, origin=None),
    Well(id="C12", x=367.56, y=49.22, has_sample=False, origin=None),
    Well(id="D1", x=267.79, y=58.29, has_sample=False, origin=None),
    Well(id="D2", x=276.86, y=58.29, has_sample=False, origin=None),
    Well(id="D3", x=285.93, y=58.29, has_sample=False, origin=None),
    Well(id="D4", x=295.00, y=58.29, has_sample=False, origin=None),
    Well(id="D5", x=304.07, y=58.29, has_sample=False, origin=None),
    Well(id="D6", x=313.14, y=58.29, has_sample=False, origin=None),
    Well(id="D7", x=322.21, y=58.29, has_sample=False, origin=None),
    Well(id="D8", x=331.28, y=58.29, has_sample=False, origin=None),
    Well(id="D9", x=340.35, y=58.29, has_sample=False, origin=None),
    Well(id="D10", x=349.42, y=58.29, has_sample=False, origin=None),
    Well(id="D11", x=358.49, y=58.29, has_sample=False, origin=None),
    Well(id="D12", x=367.56, y=58.29, has_sample=False, origin=None),
    Well(id="E1", x=267.79, y=67.36, has_sample=False, origin=None),
    Well(id="E2", x=276.86, y=67.36, has_sample=False, origin=None),
    Well(id="E3", x=285.93, y=67.36, has_sample=False, origin=None),
    Well(id="E4", x=295.00, y=67.36, has_sample=False, origin=None),
    Well(id="E5", x=304.07, y=67.36, has_sample=False, origin=None),
    Well(id="E6", x=313.14, y=67.36, has_sample=False, origin=None),
    Well(id="E7", x=322.21, y=67.36, has_sample=False, origin=None),
    Well(id="E8", x=331.28, y=67.36, has_sample=False, origin=None),
    Well(id="E9", x=340.35, y=67.36, has_sample=False, origin=None),
    Well(id="E10", x=349.42, y=67.36, has_sample=False, origin=None),
    Well(id="E11", x=358.49, y=67.36, has_sample=False, origin=None),
    Well(id="E12", x=367.56, y=67.36, has_sample=False, origin=None),
    Well(id="F1", x=267.79, y=76.43, has_sample=False, origin=None),
    Well(id="F2", x=276.86, y=76.43, has_sample=False, origin=None),
    Well(id="F3", x=285.93, y=76.43, has_sample=False, origin=None),
    Well(id="F4", x=295.00, y=76.43, has_sample=False, origin=None),
    Well(id="F5", x=304.07, y=76.43, has_sample=False, origin=None),
    Well(id="F6", x=313.14, y=76.43, has_sample=False, origin=None),
    Well(id="F7", x=322.21, y=76.43, has_sample=False, origin=None),
    Well(id="F8", x=331.28, y=76.43, has_sample=False, origin=None),
    Well(id="F9", x=340.35, y=76.43, has_sample=False, origin=None),
    Well(id="F10", x=349.42, y=76.43, has_sample=False, origin=None),
    Well(id="F11", x=358.49, y=76.43, has_sample=False, origin=None),
    Well(id="F12", x=367.56, y=76.43, has_sample=False, origin=None),
    Well(id="G1", x=267.79, y=85.5, has_sample=False, origin=None),
    Well(id="G2", x=276.86, y=85.5, has_sample=False, origin=None),
    Well(id="G3", x=285.93, y=85.5, has_sample=False, origin=None),
    Well(id="G4", x=295.00, y=85.5, has_sample=False, origin=None),
    Well(id="G5", x=304.07, y=85.5, has_sample=False, origin=None),
    Well(id="G6", x=313.14, y=85.5, has_sample=False, origin=None),
    Well(id="G7", x=322.21, y=85.5, has_sample=False, origin=None),
    Well(id="G8", x=331.28, y=85.5, has_sample=False, origin=None),
    Well(id="G9", x=340.35, y=85.5, has_sample=False, origin=None),
    Well(id="G10", x=349.42, y=85.5, has_sample=False, origin=None),
    Well(id="G11", x=358.49, y=85.5, has_sample=False, origin=None),
    Well(id="G12", x=367.56, y=85.5, has_sample=False, origin=None),
    Well(id="H1", x=267.79, y=94.57, has_sample=False, origin=None),
    Well(id="H2", x=276.86, y=94.57, has_sample=False, origin=None),
    Well(id="H3", x=285.93, y=94.57, has_sample=False, origin=None),
    Well(id="H4", x=295.00, y=94.57, has_sample=False, origin=None),
    Well(id="H5", x=304.07, y=94.57, has_sample=False, origin=None),
    Well(id="H6", x=313.14, y=94.57, has_sample=False, origin=None),
    Well(id="H7", x=322.21, y=94.57, has_sample=False, origin=None),
    Well(id="H8", x=331.28, y=94.57, has_sample=False, origin=None),
    Well(id="H9", x=340.35, y=94.57, has_sample=False, origin=None),
    Well(id="H10", x=349.42, y=94.57, has_sample=False, origin=None),
    Well(id="H11", x=358.49, y=94.57, has_sample=False, origin=None),
    Well(id="H12", x=367.56, y=94.57, has_sample=False, origin=None),
]
