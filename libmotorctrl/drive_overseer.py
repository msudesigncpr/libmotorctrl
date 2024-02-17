import asyncio
import logging
from enum import Enum
from .drive import Drive

# TODO Add locks
# TODO Add timeouts to lock acquisition
# TODO Clamp values
# TODO Refactor parse/write

CRUISE_DEPTH = (
    20_000  # Micrometers # A safe height above the board for general movement
)

CALIBRATION_OFFSET = (0, 90_000)  # Micrometers # TODO Get this from calibration


# A drive target to be used for methods which require specifying a
# target drive
class DriveTarget(Enum):
    DriveX = 0
    DriveY = 1
    DriveZ = 2


class DriveOverseer:
    def __init__(self):
        """Initialize the drives.

        Initializes the x, y and z-axis drive controllers in parallel
        by connecting to them over Modbus and spawning a worker thread
        to read and write the registers to/from the drive."""

        logging.info("Spawning drive controllers...")
        self.drive_x = Drive("X", "192.168.2.21")
        self.drive_y = Drive("Y", "192.168.2.22")
        self.drive_z = Drive("Z", "192.168.2.23")

    async def init_drives(self):
        """Initializes the drive registers to prepare them for positioning.

        On startup, the drives are not configured for motion. We must
        set a sequence of registers to clear faults, configure the
        drive for direct positioning, and enable movement."""

        async with asyncio.TaskGroup() as init_tg:
            init_tg.create_task(self.drive_x.initialize_reg())
            init_tg.create_task(self.drive_y.initialize_reg())
            init_tg.create_task(self.drive_z.initialize_reg())
        logging.info("All drives initialized")

    async def home(self, drive):
        """Homes the targeted drive.

        This method homes the target drive. It is probably desirable
        to home the z-axis drive first to avoid colliding with
        obstacles while homing the other drives."""

        match drive:
            case DriveTarget.DriveX:
                await self.drive_x.home()
            case DriveTarget.DriveY:
                await self.drive_y.home()
            case DriveTarget.DriveZ:
                await self.drive_z.home()

    async def move(self, target_x, target_y, target_z):
        """Move to the designated coordinates.

        Coordinates must be provided as um integer offsets from the
        calibration point. To execute a movement command, the system
        will raise the z-axis to the specified `CRUISE_DEPTH`, move
        the x and y axes, and then lower the z-axis to `target_z`."""

        await self.drive_z.move(CRUISE_DEPTH)
        logging.info("Drive Z raised to cruise depth")

        # Run the X and Y motions concurrently
        async with asyncio.TaskGroup() as move_tg:
            move_tg.create_task(self.drive_x.move(target_x + CALIBRATION_OFFSET[0]))
            move_tg.create_task(self.drive_y.move(target_y + CALIBRATION_OFFSET[1]))
        logging.info("XY motion complete")

        await self.drive_z.move(target_z)
        logging.info("Z motion complete")

    async def stop(self):
        """Immediately stop all movement."""

        async with asyncio.TaskGroup() as stop_tg:
            stop_tg.create_task(self.drive_x.stop())
            stop_tg.create_task(self.drive_y.stop())
            stop_tg.create_task(self.drive_z.stop())

    async def stop_drive(self, drive):
        """Immediately stop the specified drive."""

        match drive:
            case DriveTarget.DriveX:
                await self.drive_x.stop()
            case DriveTarget.DriveY:
                await self.drive_y.stop()
            case DriveTarget.DriveZ:
                await self.drive_z.stop()

    async def terminate(self):
        """Disable a drive and terminate the Modbus connection."""

        async with asyncio.TaskGroup() as term_tg:
            term_tg.create_task(self.drive_x.terminate())
            term_tg.create_task(self.drive_y.terminate())
            term_tg.create_task(self.drive_z.terminate())
