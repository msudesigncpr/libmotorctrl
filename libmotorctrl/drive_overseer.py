import logging
from enum import Enum
from .drive import Drive

# TODO Add locks
# TODO Add timeouts to lock acquisition
# TODO Clamp values
# TODO Refactor parse/write

LOGLEVEL = logging.INFO

CRUISE_DEPTH = 20_000


class DriveTarget(Enum):
    DriveX = 0
    DriveY = 1
    DriveZ = 2


class DriveOverseer:
    def __init__(self):
        logging.info("Spawning drive controllers...")
        self.drive_x = Drive("X", "192.168.2.21")
        self.drive_x.initialize()
        self.drive_x.drive_init_event.wait()
        logging.info("Drive X initialized")

        self.drive_y = Drive("Y", "192.168.2.22")
        self.drive_y.initialize()
        self.drive_y.drive_init_event.wait()
        logging.info("Drive Y initialized")

        self.drive_z = Drive("Z", "192.168.2.23")
        self.drive_z.initialize()
        self.drive_z.drive_init_event.wait()
        logging.info("Drive Z initialized")

    def home(self, drive):
        match drive:
            case DriveTarget.DriveX:
                self.drive_x.home()
                self.drive_x.drive_home_event.wait()
                logging.info("Drive X homing complete")
            case DriveTarget.DriveY:
                self.drive_y.home()
                self.drive_y.drive_home_event.wait()
                logging.info("Drive Y homing complete")
            case DriveTarget.DriveZ:
                self.drive_z.home()
                self.drive_z.drive_home_event.wait()
                logging.info("Drive Z homing complete")

    def move(self, target_x, target_y, target_z):
        self.drive_z.move(CRUISE_DEPTH)
        self.drive_z.drive_move_event.wait()
        logging.info("Drive Z raised to cruise depth")

        # TODO Do x and y motion in parallel
        self.drive_x.move(target_x)
        self.drive_x.drive_move_event.wait()
        logging.info("Drive X motion complete")

        self.drive_y.move(target_y)
        self.drive_y.drive_move_event.wait()
        self.drive_y.drive_move_event.wait()
        logging.info("Drive Y motion complete")

        self.drive_z.move(target_z)
        self.drive_z.drive_move_event.wait()
        logging.info("Drive Z motion complete")


    def terminate(self):
        self.drive_x.terminate()
        self.drive_y.terminate()
        self.drive_z.terminate()
