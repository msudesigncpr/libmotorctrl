import asyncio
import logging
from libmotorctrl import DriveOverseer, DriveTarget

LOGLEVEL = logging.INFO

logging.basicConfig(
    format="%(asctime)s: %(message)s",
    level=LOGLEVEL,
    datefmt="%H:%M:%S",
)


async def main():
    drive_ctrl = DriveOverseer()
    await drive_ctrl.init_drives()
    await drive_ctrl.home(DriveTarget.DriveZ)
    await drive_ctrl.home(DriveTarget.DriveX)
    await drive_ctrl.home(DriveTarget.DriveY)

    print("HOMING COMPLETE")

    logging.info("Motion start!")
    asyncio.create_task(drive_ctrl.move(150_000, 0, 0))
    await asyncio.sleep(2.5)
    # logging.info("STOP!")
    # await drive_ctrl.stop()
    # print("MOTION 1 COMPLETE")
    # # await drive_ctrl.move(147_000, 0, 60_000)
    # _ = input()
    # print("MOTION 2 COMPLETE")
    # await drive_ctrl.move(347_000, 100_000, 0_000)
    # print("MOTION 3 COMPLETE")
    # await drive_ctrl.move(150_000, 0, 0)
    # print("MOTION 4 COMPLETE")
    # await drive_ctrl.move(0, 0, 0)
    # print("MOTION 5 COMPLETE")
    await drive_ctrl.move(450_000, 0, 0)
    print("MOTION 6 COMPLETE")

    await drive_ctrl.terminate()


if __name__ == "__main__":
    asyncio.run(main())
