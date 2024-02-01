import logging
import time
from drive import Drive

# TODO Add locks
# TODO Add timeouts to lock acquisition
# TODO Clamp values
# TODO Refactor parse/write

LOGLEVEL = logging.INFO

CRUISE_DEPTH = 70_000

class DriveController:
    def __init__(self):
        logging.info("Spawning drive controllers...")
        drive_x = Drive("X", "192.168.2.21")
        drive_x.drive_init_event.wait()
        logging.info("Drive X initialized")

        drive_y = Drive("Y", "192.168.2.22")
        drive_y.drive_init_event.wait()
        logging.info("Drive Y initialized")

        drive_z = Drive("Z", "192.168.2.23")
        drive_z.drive_init_event.wait()
        logging.info("Drive Z initialized")
