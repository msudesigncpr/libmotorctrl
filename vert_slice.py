import csv
import logging
import sys
import time
from dataclasses import dataclass
from libmotorctrl import DriveOverseer, DriveTarget

LOGLEVEL = logging.INFO

STERILIZER_COORDINATES = (461_330, 87_950, 60_000) # Micrometers  # TODO
PETRI_DISH_DEPTH = 80_000  # Micrometers # TODO Check depth
WELL_DEPTH = 80_000  # Micrometers # TODO Check depth
# CAMERA_POS_OFFSET = 20  # Micrometers # TODO Find real value
# This is the offset of the camera from the picker head

logging.basicConfig(
    format="%(asctime)s: %(threadName)s: %(message)s",
    level=LOGLEVEL,
    datefmt="%H:%M:%S",
)


# @dataclass
# class PetriDish:
#     id: int
#     x: int
#     y: int


@dataclass
class Well:
    id: str
    x: float
    y: float
    has_sample: bool
    origin: str


@dataclass
class Colony:
    dish: str
    x: float
    y: float
    width: float
    height: float


# PETRI_DISH_COORDINATES = [
#     PetriDish(id=1, x=2600, y=-2460),
#     PetriDish(id=2, x=7100, y=-2460),
#     PetriDish(id=3, x=11600, y=-2460),
#     PetriDish(id=4, x=16100, y=-2460),
#     PetriDish(id=5, x=2600, y=2290),
#     PetriDish(id=6, x=7100, y=2290),
# ]

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


def main():
    dish_count = 4  # TODO Read in
    # num_colonies_to_sample = 96  # TODO Read in
    dwell_duration = 5
    # TODO User input setup

    logging.info("Initializing drives...")

    drive_ctrl = DriveOverseer()
    drive_ctrl.home(DriveTarget.DriveZ)
    drive_ctrl.home(DriveTarget.DriveX)
    drive_ctrl.home(DriveTarget.DriveY)

    # TODO Error propagation

    # logging.info("Collecting dish images...")
    # for i in range(dish_count):
    #    logging.info(f"Moving to dish {i}...")
    #    drive_ctrl.move(
    #        PETRI_DISH_COORDINATES[i].x - CAMERA_POS_OFFSET,
    #        PETRI_DISH_COORDINATES[i].y,
    #        60_000,
    #    )  # TODO Check depth
    #    # captureImage()

    RAW_VALID_COLONIES = [[7.220832, 9.023868], [8.166016, 3.640896]]
    # [42.471344, 8.382924], [43.456255999999996, 7.189296], [43.444704,
    # 3.926988], [41.637488, 5.545824], [39.339232, 6.281604]]

    VALID_COLONIES = []
    for colony in RAW_VALID_COLONIES:
        VALID_COLONIES.append(Colony(dish="P0", x=colony[0], y=colony[1], width=0, height=0))
        # TODO Values we don't know

    # TODO Parse text file containing colony coordinates
    # VALID_COLONIES = [
    #     Colony(dish=1, x=2659, y=2570, width=24, height=24),
    # ]

    # if len(VALID_COLONIES) > num_colonies_to_sample:
    #     target_colonies = random.sample(VALID_COLONIES, num_colonies_to_sample)
    # else:
    #     target_colonies = VALID_COLONIES
    target_colonies = VALID_COLONIES

    logging.info("Target colonies list acquired!")

    logging.info("Performing initial sterilization...")
    drive_ctrl.move(
        STERILIZER_COORDINATES[0],
        STERILIZER_COORDINATES[1],
        STERILIZER_COORDINATES[2],
    )
    logging.info(f"Sleeping for {dwell_duration} seconds...")
    time.sleep(dwell_duration)

    for colony in target_colonies:
        logging.info("Starting sampling cycle...")
        logging.info(
            f"Target colony is at {colony.x:.2f}, {colony.y:.2f} in Petri dish {colony.dish}"
        )
        well_target = None
        for well_candidate in WELLS:
            if not well_candidate.has_sample:
                well_target = well_candidate
                logging.info(f"Target well is {well_target.id}")
                break
        if well_target is None:
            logging.error("No unused wells!")  # TODO Handle differently
            sys.exit(1)
        drive_ctrl.move(int(colony.x * 10**3), int(colony.y * 10**3), PETRI_DISH_DEPTH)
        logging.info("Colony collected, moving to well...")
        # _ = input("Press any key to continue...")
        drive_ctrl.move(int(well_target.x * 10**3), int(well_target.y * 10**3), WELL_DEPTH)
        logging.info("Well reached, moving to sterilizer...")
        well_target.has_sample = True
        well_target.origin = colony.dish
        # _ = input("Press any key to continue...")
        drive_ctrl.move(
            STERILIZER_COORDINATES[0],
            STERILIZER_COORDINATES[1],
            STERILIZER_COORDINATES[2],
        )
        logging.info(f"Sleeping for {dwell_duration} seconds...")
        time.sleep(dwell_duration)

    logging.info("Sampling complete!")
    drive_ctrl.move(490_000, -90_000, 0)
    drive_ctrl.terminate()

    with open('well_locations.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow([ "Well", "Origin Petri Dish" ])
        for well in WELLS:
            if well.origin is not None:
                csvwriter.writerow([ well.id, well.origin ])


if __name__ == "__main__":
    main()
