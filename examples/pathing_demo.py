import asyncio
import json
import logging
import sys
from libmotorctrl import DriveManager, DriveTarget
from constants import *

LOGLEVEL = logging.INFO
STERILIZER_DWELL_DURATION = 5

logging.basicConfig(
    format="%(asctime)s: %(threadName)s: %(message)s",
    level=LOGLEVEL,
    datefmt="%H:%M:%S",
)


async def main():
    drive_ctrl = DriveManager()
    await drive_ctrl.init_drives()
    logging.info("Drives initialized")

    await drive_ctrl.home(DriveTarget.DriveZ)
    await drive_ctrl.home(DriveTarget.DriveX)
    await drive_ctrl.home(DriveTarget.DriveY)
    logging.info("Homing complete")

    with open("data.json", "r") as colony_file:
        valid_colonies_raw = json.load(colony_file)

    target_colonies = []
    for colony in valid_colonies_raw:
        target_colonies.append(Colony(dish="P0", x=colony[0], y=colony[1]))
        # TODO P0 is a placeholder; ideally this should come from parsing the
        # colony list so we always know which colony the sample originated from

    logging.info("Target colonies list acquired!")

    logging.info("Performing initial sterilization...")
    await drive_ctrl.move(
        STERILIZER_COORDINATES[0],
        STERILIZER_COORDINATES[1],
        STERILIZER_COORDINATES[2],
    )
    logging.info("Sleeping for %s seconds...", STERILIZER_DWELL_DURATION)
    await asyncio.sleep(STERILIZER_DWELL_DURATION)

    for colony in target_colonies:
        logging.info("Starting sampling cycle...")
        logging.info(
            f"Target colony is at {colony.x:.2f}, {colony.y:.2f} in Petri dish {colony.dish}"
        )
        # Find the target well
        well_target = None
        for well_candidate in WELLS:
            if not well_candidate.has_sample:
                well_target = well_candidate
                logging.info("Target well is %s", well_target.id)
                break
        if well_target is None:
            logging.error("No unused wells!")  # TODO Handle differently
            sys.exit(1)
        # Target well has been found, execute sampling run
        await drive_ctrl.move(
            int(colony.x * 10**3), int(colony.y * 10**3), PETRI_DISH_DEPTH
        )
        logging.info("Colony collected, moving to well...")
        await drive_ctrl.move(
            int(well_target.x * 10**3), int(well_target.y * 10**3), WELL_DEPTH
        )
        logging.info("Well reached, moving to sterilizer...")
        well_target.has_sample = True
        well_target.origin = colony.dish
        await drive_ctrl.move(
            STERILIZER_COORDINATES[0],
            STERILIZER_COORDINATES[1],
            STERILIZER_COORDINATES[2],
        )
        logging.info("Sleeping for %s seconds...", STERILIZER_DWELL_DURATION)
        await asyncio.sleep(STERILIZER_DWELL_DURATION)

    logging.info("Sampling complete!")
    await drive_ctrl.move(490_000, -90_000, 0)
    await drive_ctrl.terminate()


if __name__ == "__main__":
    asyncio.run(main())
