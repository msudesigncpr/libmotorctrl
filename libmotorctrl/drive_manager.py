"""Wrapper for all system-level drive commands via the `DriveManager` class."""

import asyncio
import logging
from enum import Enum
from .drive import Drive, DriveState, DriveError

# TODO Add locks for drive actions
# TODO Clamp position values based on calibration
# TODO Refactor parse/write to use callbacks

CRUISE_DEPTH = 20_000
"""A safe depth for the z-axis to descend to where it cannot collide with any
obstacles. Specified in micrometers.

The z-axis will be moved to this height when executing movement commands before
adjusting the x and y-axes."""

CALIBRATION_OFFSET = (0, 90_000)  # TODO Get this from calibration
"""The location of the calibration point in (x,y) format. Specified in
micrometers.

This is applied as an offset to all movement commands, before the coordinates
are sent to their respective drive controllers."""

BOUNDS = (
    (47_000, 500_000),
    (0 - CALIBRATION_OFFSET[1], 225_000 - CALIBRATION_OFFSET[1]),
)
"""The x and y-axis limits for motion.

If a movement command is issued that would move beyond these bounds,
the system will raise an exception. Data structure TBD"""


class DriveTarget(Enum):
    """A drive target used for methods which require specifying a
    target drive."""

    DriveX = 0
    DriveY = 1
    DriveZ = 2


class DriveManagerError(Exception):
    """An error raised by the drive manager."""

    pass


class DriveManager:
    """Wrapper for system-level commands to the drives.

    Generally, to use the system you will need to
    1. Create a `DriveManager` object,
    2. Initialize the drives and
    3. Home each of the drives in series

    before the system is ready to receive movement commands.

    All coordinates this class interacts with MUST be provided in micrometers.
    The drive controllers interpret the coordinates they receive as um offsets
    from the origin point set with the Festo Configuration Tool. Coordinates
    received by any methods in this class should be micrometer offsets from the
    calibration origin point, which is found by recognizing the location of the
    pinhole light with the camera.

    Once the full sampling run is complete, the drives can be disabled by
    calling the `terminate()` method."""

    def __init__(self):
        """Initialize the drives.

        Initializes the x, y and z-axis drive controllers in parallel
        by connecting to them over Modbus and spawning a worker thread
        to read and write the registers to/from the drive."""

        logging.info("Spawning drive controllers...")
        self._drive_x = Drive("X", "192.168.2.21")
        self._drive_y = Drive("Y", "192.168.2.22")
        self._drive_z = Drive("Z", "192.168.2.23")

    async def init_drives(self):
        """Initialize the drive registers to prepare them for positioning.

        On startup, the drives are not configured for motion. We must
        set a sequence of registers to clear faults, configure each
        drive for direct positioning, and enable movement."""

        async with asyncio.TaskGroup() as init_tg:
            init_tg.create_task(self._drive_x.initialize_reg())
            init_tg.create_task(self._drive_y.initialize_reg())
            init_tg.create_task(self._drive_z.initialize_reg())
        logging.info("All drives initialized")

    async def home(self, drive: DriveTarget):
        """Home the targeted drive.

        This method homes the target drive. It is probably desirable
        to home the z-axis drive first to avoid colliding with
        obstacles while homing the other drives."""

        match drive:
            case DriveTarget.DriveX:
                await self._drive_x.home()
            case DriveTarget.DriveY:
                await self._drive_y.home()
            case DriveTarget.DriveZ:
                await self._drive_z.home()

    async def move(self, target_x: int, target_y: int, target_z: int):
        """Move to the designated coordinates.

        Coordinates must be provided as um integer offsets from the
        calibration point. To execute a movement command, the system
        will raise the z-axis to the specified `CRUISE_DEPTH`, move
        the x and y axes, and then lower the z-axis to `target_z`."""

        try:
            if not (BOUNDS[0][0] <= target_x <= BOUNDS[0][1]):
                raise DriveManagerError("X coordinate exceeds limits")

            if not (BOUNDS[1][0] <= target_y <= BOUNDS[1][1]):
                raise DriveManagerError("Y coordinate exceeds limits")
        except DriveManagerError as e:
            logging.critical("Unhandled error '%s', terminating...", e)
            await self.terminate()
            raise

        await self._drive_z.move(CRUISE_DEPTH)
        logging.info("Drive Z raised to cruise depth")

        # Run the X and Y motions concurrently
        async with asyncio.TaskGroup() as move_tg:
            move_tg.create_task(self._drive_x.move(target_x + CALIBRATION_OFFSET[0]))
            move_tg.create_task(self._drive_y.move(target_y + CALIBRATION_OFFSET[1]))
        logging.info("XY motion complete")

        await self._drive_z.move(target_z)
        logging.info("Z motion complete")

    async def stop(self):
        """Immediately stop all movement.

        This sets the halt bit on all drives. This can be reversed
        using the `resume()` method."""

        async with asyncio.TaskGroup() as stop_tg:
            stop_tg.create_task(self._drive_x.stop())
            stop_tg.create_task(self._drive_y.stop())
            stop_tg.create_task(self._drive_z.stop())

    async def stop_drive(self, drive: DriveTarget):
        """Immediately stop the specified drive.

        This sets the halt bit on the drive. This can be reversed
        using the `resume_drive()` method."""

        match drive:
            case DriveTarget.DriveX:
                await self._drive_x.stop()
            case DriveTarget.DriveY:
                await self._drive_y.stop()
            case DriveTarget.DriveZ:
                await self._drive_z.stop()

    async def resume(self):
        """Clear the halt bit on all drives."""

        async with asyncio.TaskGroup() as resume_tg:
            resume_tg.create_task(self._drive_x.resume())
            resume_tg.create_task(self._drive_y.resume())
            resume_tg.create_task(self._drive_z.resume())

    async def resume_drive(self, drive: DriveTarget):
        """Clear the halt bit on the specified drive."""

        match drive:
            case DriveTarget.DriveX:
                await self._drive_x.resume()
            case DriveTarget.DriveY:
                await self._drive_y.resume()
            case DriveTarget.DriveZ:
                await self._drive_z.resume()

    def get_position(self) -> (float, float, float):
        """Get the position of the picker-head in millimeters.

        This is measured by the encoders in each drive, and is an
        offset from the calibration point."""

        x_pos = (self._drive_x.get_encoder_position() - CALIBRATION_OFFSET[0]) / 1000
        y_pos = (self._drive_y.get_encoder_position() - CALIBRATION_OFFSET[1]) / 1000
        z_pos = (self._drive_z.get_encoder_position()) / 1000
        return (x_pos, y_pos, z_pos)

    def get_drive_state(self, drive: DriveTarget) -> DriveState:
        """Get the status of a drive.

        Note that if the drive state is `DriveState.WARN` the drive
        may still be capable of movement depending on the severity of
        the warning."""

        match drive:
            case DriveTarget.DriveX:
                return self._drive_x.get_status()
            case DriveTarget.DriveY:
                return self._drive_y.get_status()
            case DriveTarget.DriveZ:
                return self._drive_z.get_status()

    def get_drive_exception(self, drive: DriveTarget) -> DriveError:
        """Get the diagnostic code and message from a drive.

        Refer to Appendix D of the CMMO-ST FHPP datasheet for a
        comprehensive list of error codes and diagnostic messages. If
        no fault is present, the error code will be 0."""

        match drive:
            case DriveTarget.DriveX:
                return self._drive_x.get_exception()
            case DriveTarget.DriveY:
                return self._drive_y.get_exception()
            case DriveTarget.DriveZ:
                return self._drive_z.get_exception()

    async def reset_drive(self, drive: DriveTarget):
        """Reset a targeted drive, acknowledging faults.

        Some error messages are acknowledgeable, and can be cleared by
        toggling the reset bit on the problematic drive controller."""

        match drive:
            case DriveTarget.DriveX:
                return self._drive_x.reset_error()
            case DriveTarget.DriveY:
                return self._drive_y.reset_error()
            case DriveTarget.DriveZ:
                return self._drive_z.reset_error()

    async def terminate(self):
        """Disable all drives and terminate the Modbus connections."""

        async with asyncio.TaskGroup() as term_tg:
            term_tg.create_task(self._drive_x.terminate())
            term_tg.create_task(self._drive_y.terminate())
            term_tg.create_task(self._drive_z.terminate())
