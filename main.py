import logging
import time
from drive import Drive

# TODO Add locks
# TODO Add timeouts to lock acquisition
# TODO Clamp values
LOGLEVEL = logging.INFO
TARGETS = [
    (0, 0, 80_000),
    (50_000, 50_000, 100_000),
    (50_000, 50_000, 80_000),
    (200_000, 200_000, 100_000),
    (200_000, 200_000, 80_000),
    (0, 0, 0),
]


def xy_move(drive_x, drive_y, target_x, target_y):
    logging.info("Setting target XY position to (%s, %s) [um]...", target_x, target_y)
    drive_x.reg_control["setpoint"] = target_x
    drive_y.reg_control["setpoint"] = target_y
    time.sleep(0.2)

    logging.info("Starting XY motion...")
    drive_x.reg_control["positioning_start"] = True
    drive_y.reg_control["positioning_start"] = True
    time.sleep(0.4)

    while (
        not drive_x.reg_status["motion_complete"]
        or not drive_y.reg_status["motion_complete"]
    ):
        time.sleep(0.1)
    drive_x.reg_control["positioning_start"] = False
    drive_y.reg_control["positioning_start"] = False
    logging.info("Drive XY positioning complete!")


def z_move(drive_z, target_z):
    logging.info("Setting target Z position to %s um...", target_z)
    drive_z.reg_control["setpoint"] = target_z
    time.sleep(0.2)

    logging.info("Starting Z motion...")
    drive_z.reg_control["positioning_start"] = True
    time.sleep(0.4)

    while not drive_z.reg_status["motion_complete"]:
        time.sleep(0.1)
    drive_z.reg_control["positioning_start"] = False
    logging.info("Drive Z positioning complete!")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s: %(threadName)s: %(message)s",
        level=LOGLEVEL,
        datefmt="%H:%M:%S",
    )

    logging.info("Spawning drive controllers...")
    drive_x = Drive("X", "192.168.2.21")
    drive_y = Drive("Y", "192.168.2.22")
    drive_z = Drive("Z", "192.168.2.23")

    drive_x.drive_init_event.wait()
    logging.info("Drive X initialized")
    drive_y.drive_init_event.wait()
    logging.info("Drive Y initialized")
    drive_z.drive_init_event.wait()
    logging.info("Drive Z initialized")

    for target in TARGETS:
        xy_move(drive_x, drive_y, target[0], target[1])
        z_move(drive_z, target[2])

    logging.info("Terminating workers...")
    drive_x.terminate()
    drive_y.terminate()
    drive_z.terminate()
    logging.info("Program complete")
