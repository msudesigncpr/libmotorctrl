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

print("HOMING COMPLETE")

drive_ctrl.move(0, 194_000, 60_000)
print("MOTION 1 COMPLETE")
drive_ctrl.move(147_000, 0, 60_000)
print("MOTION 2 COMPLETE")
drive_ctrl.move(347_000, 150_000, 40_000)
print("MOTION 3 COMPLETE")
drive_ctrl.move(450_000, 0, 0)
print("MOTION 4 COMPLETE")

drive_ctrl.terminate()
