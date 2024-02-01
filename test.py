import logging
from libmotorctrl import DriveController, DriveTarget

LOGLEVEL = logging.INFO

logging.basicConfig(
    format="%(asctime)s: %(threadName)s: %(message)s",
    level=LOGLEVEL,
    datefmt="%H:%M:%S",
)

drive_ctrl = DriveController()
drive_ctrl.home(DriveTarget.DriveZ)
drive_ctrl.home(DriveTarget.DriveX)
drive_ctrl.home(DriveTarget.DriveY)

drive_ctrl.terminate()
