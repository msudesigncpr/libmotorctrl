import logging
import time
from drive import Drive

# TODO Add locks
# TODO Add timeouts to lock acquisition
# TODO Clamp values
# TODO Refactor parse/write

LOGLEVEL = logging.INFO

CRUISE_DEPTH = 70_000
# DRILL_DEPTH = 72_500

TARGETS = [
        (0, 0, 80_000),
        (459_000, 194_000, 87_000),
        (33_000, 43_000, 82_000),
        (40_000, 100_000, 84_000),
        (459_000, 194_000, 87_000),
        (140_000, 60_000, 82_000),
        (347_000, 60_000, 82_000),
        (459_000, 194_000, 87_000),
        (250_000, 60_000, 82_000),
        (450_000, 165_000, 86_000),
        (459_000, 194_000, 87_000),
        (133_000, 186_000, 87_000),
        (347_000, 60_000, 82_000),
        (459_000, 194_000, 87_000),
        (240_000, 186_000, 87_000),
        (40_000, 100_000, 84_000),
        (459_000, 194_000, 87_000),
        (347_000, 186_000, 87_000),
        (450_000, 165_000, 86_000),
        (459_000, 194_000, 87_000),
        ]


def move(drive_x, drive_y, drive_z, target_x, target_y, target_z):
    logging.info("Setting target position to (%s, %s, %s) [um]...", target_x, target_y, target_z)

    z_move(drive_z, CRUISE_DEPTH)

    drive_x.reg_control.setpoint = target_x
    drive_y.reg_control.setpoint = target_y
    time.sleep(0.2)

    logging.info("Starting XY motion...")
    drive_x.reg_control.positioning_start = True
    drive_y.reg_control.positioning_start = True
    time.sleep(0.4)

    while (
        not drive_x.reg_status.motion_complete
        or not drive_y.reg_status.motion_complete
    ):
        time.sleep(0.1)
    drive_x.reg_control.positioning_start = False
    drive_y.reg_control.positioning_start = False
    logging.info("Drive XY positioning complete!")

    z_move(drive_z, target_z)


def z_move(drive_z, target_z):
    logging.info("Setting target Z position to %s um...", target_z)
    drive_z.reg_control.setpoint = target_z
    time.sleep(0.2)

    logging.info("Starting Z motion...")
    drive_z.reg_control.positioning_start = True
    time.sleep(0.4)

    while not drive_z.reg_status.motion_complete:
        time.sleep(0.1)
    drive_z.reg_control.positioning_start = False
    logging.info("Drive Z positioning complete!")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s: %(threadName)s: %(message)s",
        level=LOGLEVEL,
        datefmt="%H:%M:%S",
    )

    logging.info("Spawning drive controllers...")
    drive_z = Drive("Z", "192.168.2.23")
    drive_x = Drive("X", "192.168.2.21")
    drive_y = Drive("Y", "192.168.2.22")

    drive_z.drive_init_event.wait()
    logging.info("Drive Z initialized")
    drive_x.drive_init_event.wait()
    logging.info("Drive X initialized")
    drive_y.drive_init_event.wait()
    logging.info("Drive Y initialized")

    _ = input()
    for target in TARGETS:
        start_time = time.time()
        move(drive_x, drive_y, drive_z, target[0], target[1], target[2])
        duration = time.time() - start_time
        print("Duration: {:.2f}".format(duration))
        _ = input()

    logging.info("Terminating workers...")
    drive_x.terminate()
    drive_y.terminate()
    drive_z.terminate()
    logging.info("Program complete")
