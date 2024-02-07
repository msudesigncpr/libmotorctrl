import logging
import random
import sys
import time
from dataclasses import dataclass
from libmotorctrl import DriveOverseer, DriveTarget

LOGLEVEL = logging.INFO

STERILIZER_COORDINATES = (18160, 3460, 60)  # TODO Check depth
PETRI_DISH_DEPTH = 80_000  # TODO Check depth
WELL_DEPTH = 80_000  # TODO Check depth
CAMERA_POS_OFFSET = 20  # TODO Find real value
# This is the offset of the camera from the picker head

logging.basicConfig(
    format="%(asctime)s: %(threadName)s: %(message)s",
    level=LOGLEVEL,
    datefmt="%H:%M:%S",
)


@dataclass
class PetriDish:
    id: int
    x: int
    y: int


@dataclass
class Well:
    id: int
    x: int
    y: int
    has_sample: bool
    origin: int


@dataclass
class Colony:
    dish: int
    x: int
    y: int
    width: float
    height: float


PETRI_DISH_COORDINATES = [
    PetriDish(id=1, x=2600, y=-2460),
    PetriDish(id=2, x=7100, y=-2460),
    PetriDish(id=3, x=11600, y=-2460),
    PetriDish(id=4, x=16100, y=-2460),
    PetriDish(id=5, x=2600, y=2290),
    PetriDish(id=6, x=7100, y=2290),
]

WELL_COORDINATES = [
    Well(id=1, x=0, y=0, has_sample=False, origin=None),  # TODO
    Well(id=2, x=0, y=0, has_sample=False, origin=None),  # TODO
    Well(id=3, x=0, y=0, has_sample=False, origin=None),  # TODO
    Well(id=4, x=0, y=0, has_sample=False, origin=None),  # TODO
    Well(id=5, x=0, y=0, has_sample=False, origin=None),  # TODO
    Well(id=6, x=0, y=0, has_sample=False, origin=None),  # TODO
    Well(id=7, x=0, y=0, has_sample=False, origin=None),  # TODO
    Well(id=8, x=0, y=0, has_sample=False, origin=None),  # TODO
    Well(id=9, x=0, y=0, has_sample=False, origin=None),  # TODO
    Well(id=10, x=0, y=0, has_sample=False, origin=None),  # TODO
    Well(id=11, x=0, y=0, has_sample=False, origin=None),  # TODO
]


def main():
    dish_count = 4  # TODO Read in
    num_colonies_to_sample = 96  # TODO Read in
    dwell_duration = 5
    # TODO User input setup

    logging.info("Initializing drives...")

    drive_ctrl = DriveOverseer()
    drive_ctrl.home(DriveTarget.DriveZ)
    drive_ctrl.home(DriveTarget.DriveX)
    drive_ctrl.home(DriveTarget.DriveY)

    # TODO Error propagation

    logging.info("Collecting dish images...")
    for i in range(dish_count):
        logging.info(f"Moving to dish {i}...")
        drive_ctrl.move(
            PETRI_DISH_COORDINATES[i].x - CAMERA_POS_OFFSET,
            PETRI_DISH_COORDINATES[i].y,
            60_000,
        )  # TODO Check depth
        # captureImage()

    # TODO Parse text file containing colony coordinates
    VALID_COLONIES = [
        Colony(dish=1, x=2659, y=2570, width=24, height=24),
    ]

    if len(VALID_COLONIES) > num_colonies_to_sample:
        TARGET_COLONIES = random.sample(VALID_COLONIES, num_colonies_to_sample)
    else:
        TARGET_COLONIES = VALID_COLONIES

    for colony in TARGET_COLONIES:
        logging.info("Starting sampling cycle...")
        logging.info(
            f"Target colony is at {colony.x}, {colony.y} in Petri dish {colony.dish}"
        )
        well_target = None
        for well_candidate in WELL_COORDINATES:
            if not well_candidate.has_sample:
                well_target = well_candidate
                logging.info(f"Target well is {well_target.id}")
                break
        if well_target is None:
            logging.error("No unused wells!")  # TODO Handle differently
            sys.exit(1)
        drive_ctrl.move(colony.x, colony.y, PETRI_DISH_DEPTH)
        drive_ctrl.move(well_target.x, well_target.y, WELL_DEPTH)
        well_target.has_sample = True
        well_target.origin = colony.dish
        drive_ctrl.move(
            STERILIZER_COORDINATES[0],
            STERILIZER_COORDINATES[1],
            STERILIZER_COORDINATES[2],
        )
        time.sleep(dwell_duration)

    logging.info("Sampling complete!")
    drive_ctrl.terminate()

    # TODO Store result
    # Have populated list of wells with origins


if __name__ == "__main__":
    main()
