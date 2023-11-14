import logging
import time
from drive import Drive

# TODO Add locks
# TODO Add timeouts to lock acquisition
# TODO Clamp values


# Target coordinates in um
def xy_move(drive_x, drive_y, target_x, target_y):
    logging.info("Setting target position to (%s, %s)...", target_x, target_y)
    drive_x.reg_control["setpoint"] = target_x
    drive_y.reg_control["setpoint"] = target_y
    time.sleep(0.2)

    logging.info("Starting motion...")
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
    logging.info("Drive X & Y positioning complete!")


# Target coordinates in um
def z_move(drive_z, target_z):
    logging.info("Setting target Z position to %s...", target_z)
    drive_z.reg_control["setpoint"] = target_z
    time.sleep(0.2)

    logging.info("Starting motion...")
    drive_z.reg_control["positioning_start"] = True
    time.sleep(0.4)

    while not drive_z.reg_status["motion_complete"]:
        time.sleep(0.1)
    drive_z.reg_control["positioning_start"] = False
    logging.info("Drive Z positioning complete!")


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("Main: Spawning drive controllers...")
    drive_x = Drive("X", "192.168.2.21")
    drive_y = Drive("Y", "192.168.2.22")
    drive_z = Drive("Z", "192.168.2.23")

    drive_x.drive_init_event.wait()
    logging.info("Main : Drive X initialized")
    drive_y.drive_init_event.wait()
    logging.info("Main : Drive Y initialized")
    drive_z.drive_init_event.wait()
    logging.info("Main : Drive Z initialized")

    z_move(drive_z, 80000)

    xy_move(drive_x, drive_y, 50000, 50000)

    z_move(drive_z, 100000)
    _ = input()
    z_move(drive_z, 80000)

    xy_move(drive_x, drive_y, 200000, 200000)

    z_move(drive_z, 100000)
    _ = input()
    z_move(drive_z, 80000)

    xy_move(drive_x, drive_y, 0, 0)
    z_move(drive_z, 0)

    logging.info("Terminating workers...")
    drive_x.terminate()
    drive_y.terminate()
    drive_z.terminate()
    logging.info("Program complete")
