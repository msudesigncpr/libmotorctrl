import logging
from libmotorctrl import DriveOverseer, DriveTarget

LOGLEVEL = logging.INFO

logging.basicConfig(
    format="%(asctime)s: %(threadName)s: %(message)s",
    level=LOGLEVEL,
    datefmt="%H:%M:%S",
)

drive_ctrl = DriveOverseer()
drive_ctrl.home(DriveTarget.DriveZ)
drive_ctrl.home(DriveTarget.DriveX)
drive_ctrl.home(DriveTarget.DriveY)

drive_ctrl.move(0, 194_000, 60_000)
drive_ctrl.move(347_000, 194_000, 60_000)
drive_ctrl.move(347_000, 0, 40_000)
drive_ctrl.move(347_000, 0, 0)

drive_ctrl.terminate()
