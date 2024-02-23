import asyncio
import logging
from libmotorctrl import DriveManager, DriveTarget, DriveActionError
import sys

LOGLEVEL = logging.INFO

logging.basicConfig(
    format="%(asctime)s: %(message)s",
    level=LOGLEVEL,
    datefmt="%H:%M:%S",
)


async def main():
    drive_ctrl = DriveManager()
    await drive_ctrl.init_drives()
    logging.info("Drives initialized")

    logging.info("S: %s", drive_ctrl.get_drive_state(DriveTarget.DriveX))

    await drive_ctrl.home(DriveTarget.DriveZ)
    await drive_ctrl.home(DriveTarget.DriveX)
    await drive_ctrl.home(DriveTarget.DriveY)
    logging.info("S: %s", drive_ctrl.get_drive_state(DriveTarget.DriveX))
    logging.info("Homing complete")

    logging.info("Motion start!")
    task = asyncio.create_task(drive_ctrl.move(150_000, 0, 0))
    await asyncio.sleep(2.5)
    logging.info("Done sleeping")
    logging.info("S: %s", drive_ctrl.get_drive_state(DriveTarget.DriveX))
    try:
        await task
    except DriveActionError as e:
        logging.error("Drive error: %s", e)
        sys.exit(1)
    logging.warning("Encoder says: %s", drive_ctrl.get_position())
    _ = input()
    # logging.info("Motion 1 complete")
    # await drive_ctrl.move(347_000, 100_000, 60_000)
    # logging.info("Motion 2 complete")
    # await drive_ctrl.move(150_000, 0, 60_000)
    # logging.info("Motion 3 complete")
    # await drive_ctrl.move(0, 0, 60_000)
    # logging.info("Motion 4 complete")
    try:
        await drive_ctrl.move(495_000, -90_000, 0)
    except DriveActionError as e:
        logging.error("Drive error: %s", e)
        sys.exit(1)
    logging.info("Motion 5 complete")
    logging.info("S: %s", drive_ctrl.get_drive_state(DriveTarget.DriveX))

    logging.info("Shutting down...")
    await drive_ctrl.terminate()
    logging.info("S: %s", drive_ctrl.get_drive_state(DriveTarget.DriveX))
    logging.info("Drive connections terminated")


if __name__ == "__main__":
    asyncio.run(main())
