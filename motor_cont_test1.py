import logging
import time
from drive import Drive

# TODO Add locks
# TODO Add timeouts to lock acquisition
# TODO Clamp values

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("Main: Spawning drive controllers...")
    drive_x = Drive("X", "192.168.2.21")
    drive_y = Drive("Y", "192.168.2.22")
    drive_z = Drive("Z", "192.168.2.23")

    drive_x.drive_init_event.wait()
    logging.info("Main : Drive X initialized; main thread awake")
    drive_y.drive_init_event.wait()
    logging.info("Main : Drive Y initialized; main thread awake")
    drive_z.drive_init_event.wait()
    logging.info("Main : Drive Z initialized; main thread awake")

    logging.info("Setting target position to 10000...")
    drive_y.reg_control["setpoint"] = 10000
    time.sleep(0.2)

    logging.info("Starting motion...")
    drive_y.reg_control["positioning_start"] = True
    time.sleep(0.4)

    while not drive_y.reg_status["motion_complete"]:
        time.sleep(0.1)
    drive_y.reg_control["positioning_start"] = False
    logging.info("Drive Y positioning complete!")

    logging.info("Setting target position to 0...")
    drive_y.reg_control["setpoint"] = 0
    time.sleep(0.2)

    logging.info("Starting motion...")
    drive_y.reg_control["positioning_start"] = True
    time.sleep(0.4)

    while not drive_y.reg_status["motion_complete"]:
        time.sleep(0.1)
    drive_y.reg_control["positioning_start"] = False
    logging.info("Drive Y positioning complete!")

    logging.info("Terminating workers...")
    drive_x.terminate()
    drive_y.terminate()
    drive_z.terminate()
    logging.info("Program complete")
