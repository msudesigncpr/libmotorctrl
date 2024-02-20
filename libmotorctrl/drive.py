import asyncio
import logging
import threading
import time
from enum import Enum, IntEnum
from dataclasses import dataclass
from pymodbus.client import ModbusTcpClient

logging.getLogger("pymodbus").setLevel(logging.WARNING)

# The `OpMode`, `SetpointMode` and `ControlMode` enums (and their
# values) are all derived from the CMMO-ST device profile FHPP
# datasheet and directly correspond with register values specified on
# the pages referenced below.


class OpMode(IntEnum):
    """@private"""

    # See page 42, Table 5.14, B6-B7
    # See page 46, Table 5.21, B6-B7
    RECSELECT = 0b0000
    DIRECTAPP = 0b0001
    RESERVED1 = 0b0010
    RESERVED2 = 0b0011


class SetpointMode(IntEnum):
    """@private"""

    # See page 44, Table 5.16, B0
    # See page 48, Table 5.24, B0
    ABSOLUTE = 0
    RELATIVE = 1


class ControlMode(IntEnum):
    """@private"""

    # See page 44, Table 5.16, B1-B2
    # See page 48, Table 5.24, B1-B2
    POSITIONING = 0b00
    POWER = 0b01
    SPEED = 0b10
    RESERVED = 0b11


class DriveState(Enum):
    """The status of the drive controller."""

    READY = 0
    """Drive has no faults or warnings and is ready for movement."""
    WARN = 1
    """There are no error present, but there is a warning. The drive
    may or may not still be able to move."""
    ERROR = 2
    """An error is present. The drive will not move."""
    NOHOME = 3
    """Drive has no faults or warnings, but has no homing reference set."""
    HALT = 4
    """Drive operation is enabled, but the halt bit is set, disabling the drive."""
    DISABLED = 99
    """Drive operation is not enabled."""


class DriveActionError(Exception):
    """An error raised by a drive interface method."""

    pass


class DriveError:
    """An error code and description read from the drive controller.

    Error codes and descriptions are from the CMMO-ST FHPP datasheet,
    Appendix D."""

    def __init__(self, error_code: int, error_desc: str):
        self.error_code = error_code
        self.error_desc = error_desc


# The CMMO-ST drive constrollers have separate control registers (write-only)
# and status registers (read-only). They are subtly different. Consult section
# 5.4 of the CMMO-ST FHPP datasheet for details on the mapping.

# The classes defined below contain the full contents of these registers.


@dataclass(slots=True)
class ControlRegisters:
    """The control registers written to the drive controller.

    @private"""

    # CCONT
    drive_enabled: bool
    operation_enabled: bool
    brake_active: bool
    reset: bool
    fct_blocked: bool
    operation_mode: OpMode
    # CPOS
    halt_active: bool
    positioning_start: bool
    homing_start: bool
    jog_positive: bool
    jog_negative: bool
    teach: bool
    clear_path: bool
    # CDIR
    setpoint_mode: SetpointMode
    control_mode: ControlMode
    stroke_limit_bypass: bool
    # SP 1
    preselection: int
    # SP 2
    setpoint: int


@dataclass(slots=True)
class StatusRegisters:
    """The status registers read from the drive controller.

    @private"""

    # SCON
    drive_enabled: bool
    operation_enabled: bool
    warning_present: bool
    fault_present: bool
    load_applied: bool
    fct_blocked: bool
    operation_mode: OpMode
    # SPOS
    halt_active: bool
    ack_start: bool
    motion_complete: bool
    ack_teach: bool
    is_moving: bool
    following_error: bool
    still_monitoring: bool
    reference_set: bool
    # SDIR
    setpoint_mode: SetpointMode
    control_mode: ControlMode
    speed_limit_reached: bool
    stroke_limit_reached: bool
    # Drive actual velocity (%)
    velocity_percent: int
    # Drive actual position (sinc)
    position: int


class Drive:
    """Object representing an active drive controller.

    A worker thread is spawned for each drive controller to continually
    read/write the registers values (from the `ControlRegisters` and
    `StatusRegisters` classes defined above). The methods within this class
    operate by updating the internal `ControlRegisters` object, then waiting
    for the worker thread to write the register values out to the controller.

    The worker thread is defined by the `worker()` method.

    @private"""

    def __init__(self, name: str, ip_addr: str):
        self.name = name
        self.ip_addr = ip_addr
        self.terminated = False
        self.client = ModbusTcpClient(ip_addr)
        self.error_code = None
        self.reg_control = ControlRegisters(
            # CCON
            drive_enabled=False,
            operation_enabled=False,
            brake_active=True,
            reset=False,
            fct_blocked=False,
            operation_mode=OpMode.RECSELECT,
            # CPOS
            halt_active=True,
            positioning_start=False,
            homing_start=False,
            jog_positive=False,
            jog_negative=False,
            teach=False,
            clear_path=False,
            # CDIR
            setpoint_mode=SetpointMode.ABSOLUTE,
            control_mode=ControlMode.POSITIONING,
            stroke_limit_bypass=False,
            # SP 1
            preselection=0,
            # SP 2
            setpoint=0,
        )
        self.reg_status = StatusRegisters(
            # SCON
            drive_enabled=False,
            operation_enabled=False,
            warning_present=False,
            fault_present=False,
            load_applied=False,
            fct_blocked=False,
            operation_mode=OpMode.RECSELECT,
            # SPOS
            halt_active=True,
            ack_start=False,
            motion_complete=False,
            ack_teach=False,
            is_moving=False,
            following_error=False,
            still_monitoring=False,
            reference_set=False,
            # SDIR
            setpoint_mode=SetpointMode.ABSOLUTE,
            control_mode=ControlMode.POSITIONING,
            speed_limit_reached=False,
            stroke_limit_reached=False,
            # Drive actual velocity (%)
            velocity_percent=0,
            # Drive actual position (sinc)
            position=0,
        )

        self.client.connect()
        logging.debug("Client is connected!")

        logging.debug("Initializing write thread...")
        self.write_worker = threading.Thread(target=self.worker, name=self.name)
        logging.debug("Starting write thread...")
        self.write_worker.start()

    async def initialize_reg(self):
        await asyncio.sleep(0.2)

        logging.debug("Enabling drive...")
        self.reg_control.drive_enabled = True
        await asyncio.sleep(0.2)

        logging.debug("Disabling stop...")
        self.reg_control.operation_enabled = True
        await asyncio.sleep(0.2)

        logging.debug("Disabling halt...")
        self.reg_control.halt_active = False
        await asyncio.sleep(0.2)

        logging.debug("Disabling brake...")
        self.reg_control.brake_active = False
        await asyncio.sleep(0.2)

        logging.debug("Clearing faults...")
        self.reg_control.reset = True
        await asyncio.sleep(0.2)

        logging.debug("De-asserting reset...")
        self.reg_control.reset = False
        await asyncio.sleep(0.2)

        logging.debug("Setting operation mode to direct application...")
        self.reg_control.operation_mode = OpMode.DIRECTAPP
        self.reg_control.preselection = 100
        await asyncio.sleep(0.2)

        logging.info("Drive %s initialized", self.name)

    async def home(self):
        logging.debug("Starting homing...")
        self.reg_control.homing_start = True
        await asyncio.sleep(0.2)
        self.reg_control.homing_start = False
        await asyncio.sleep(0.4)

        while not self.reg_status.motion_complete:
            await asyncio.sleep(0.1)
        logging.info("Drive %s homing complete", self.name)

    async def move(self, target: int):
        self.reg_control.setpoint = target
        await asyncio.sleep(0.2)

        logging.debug("%s: Setpoint is %s", self.name, self.reg_control.setpoint)
        self.reg_control.positioning_start = True
        await asyncio.sleep(0.4)
        self.reg_control.positioning_start = False
        await asyncio.sleep(0.2)

        while not self.reg_status.motion_complete:
            await asyncio.sleep(0.1)
            logging.debug("%s: Waiting for motion to complete...", self.name)
            if self.get_status() == DriveState.ERROR:
                raise DriveActionError("Movement aborted!")

        logging.debug("%s: Drive positioning complete!", self.name)

    async def terminate(self):
        self.reg_control.drive_enabled = False
        self.reg_control.operation_enabled = False
        self.reg_control.halt_active = True
        self.reg_control.brake_active = True
        self.reg_control.reset = True
        await asyncio.sleep(0.4)
        self.terminated = True
        await asyncio.sleep(0.2)
        self.write_worker.join()
        self.client.close()

    def reg_read(self):
        result = self.client.read_holding_registers(0x0, 0x4)

        if result.isError():
            logging.error("Modbus read response was an error!")
            raise DriveActionError("Invalid drive response")
        else:
            # Parse SCON
            self.reg_status.drive_enabled = bool(((result.registers[0] >> 0) >> 8) & 1)
            self.reg_status.operation_enabled = bool(
                ((result.registers[0] >> 1) >> 8) & 1
            )
            self.reg_status.warning_present = bool(
                ((result.registers[0] >> 2) >> 8) & 1
            )
            self.reg_status.fault_present = bool(((result.registers[0] >> 3) >> 8) & 1)
            self.reg_status.load_applied = bool(((result.registers[0] >> 4) >> 8) & 1)
            self.reg_status.fct_blocked = bool(((result.registers[0] >> 5) >> 8) & 1)
            self.reg_status.operation_mode = int((result.registers[0] >> 6) >> 8)

            # Parse SPOS
            self.reg_status.halt_active = not bool((result.registers[0] >> 0) & 1)
            self.reg_status.ack_start = bool((result.registers[0] >> 1) & 1)
            self.reg_status.motion_complete = bool((result.registers[0] >> 2) & 1)
            self.reg_status.ack_teach = bool((result.registers[0] >> 3) & 1)
            self.reg_status.is_moving = bool((result.registers[0] >> 4) & 1)
            self.reg_status.following_error = bool((result.registers[0] >> 5) & 1)
            self.reg_status.still_monitoring = bool((result.registers[0] >> 6) & 1)
            self.reg_status.reference_set = bool((result.registers[0] >> 7) & 1)

            # Parse SDIR
            self.reg_status.setpoint_mode = int(((result.registers[1] >> 0) >> 8) & 1)
            self.reg_status.control_mode = int(((result.registers[1] >> 1) >> 8) & 0b11)
            self.reg_status.speed_limit_reached = bool(
                ((result.registers[1] >> 4) >> 8) & 1
            )
            self.reg_status.stroke_limit_reached = bool(
                ((result.registers[1] >> 5) >> 8) & 1
            )
            # Drive actual velocity (%)
            self.reg_status.velocity_percent = int(result.registers[1] & 0xFFFF)
            # Drive actual position (sinc)
            self.reg_status.position = int(
                (result.registers[2] << 16) + result.registers[3]
            )

            logging.debug("Parsed device register state is %s", self.reg_status)

    def reg_write(self):
        register_out = [0x0000, 0x0000, 0x0000, 0x0000]

        # CCON
        register_out[0] |= (int(self.reg_control.drive_enabled) << 0) << 8
        register_out[0] |= (int(self.reg_control.operation_enabled) << 1) << 8
        register_out[0] |= (int(not self.reg_control.brake_active) << 2) << 8
        register_out[0] |= (int(self.reg_control.reset) << 3) << 8
        register_out[0] |= (int(self.reg_control.fct_blocked) << 5) << 8
        register_out[0] |= (int(self.reg_control.operation_mode) << 6) << 8

        # CPOS
        register_out[0] |= int(not self.reg_control.halt_active) << 0
        register_out[0] |= int(self.reg_control.positioning_start) << 1
        register_out[0] |= int(self.reg_control.homing_start) << 2
        register_out[0] |= int(self.reg_control.jog_positive) << 3
        register_out[0] |= int(self.reg_control.jog_negative) << 4
        register_out[0] |= int(self.reg_control.teach) << 5
        register_out[0] |= int(self.reg_control.clear_path) << 6

        # CDIR
        register_out[1] |= (int(self.reg_control.setpoint_mode) << 0) << 8
        register_out[1] |= (int(self.reg_control.control_mode) << 1) << 8
        register_out[1] |= (int(self.reg_control.stroke_limit_bypass) << 5) << 8

        # SP 1
        register_out[1] |= self.reg_control.preselection

        # SP 2
        register_out[2] |= self.reg_control.setpoint >> 16
        register_out[3] |= self.reg_control.setpoint & 0xFFFF
        logging.debug("Raw register write buffer: %s", register_out)

        result = self.client.write_registers(0x0, register_out)
        if result.isError():
            logging.error("Modbus write response was an error!")
            raise DriveActionError("Invalid drive write acknowledge")

    def read_exception(self):
        logging.debug("Reading exception status...")
        result = self.client.read_exception_status()
        self.error_code = result.encode()
        logging.debug("Exception code: %s", self.error_code)

    def get_pos_mm(self) -> float:
        return self.reg_status.position * 7.93
        # TODO Find constant formula

    def get_status(self) -> DriveState:
        """Identify the drive state from the status registers."""
        if self.reg_status.fault_present:
            return DriveState.ERROR
        elif self.reg_status.warning_present:
            return DriveState.WARN
        elif not self.reg_status.reference_set:
            return DriveState.NOHOME
        elif self.reg_status.drive_enabled and self.reg_status.operation_enabled:
            if self.reg_status.halt_active:
                return DriveState.HALT
            else:
                return DriveState.READY
        else:
            return DriveState.DISABLED

    def get_exception(self) -> DriveError:
        """Match the drive error to an exception code."""

        # TODO Get the other error messages
        match self.error_code:
            case bytes.fromhex("00"):
                error_desc = "N/A"
            case bytes.fromhex("01"):
                error_desc = "Software error"
            case bytes.fromhex("02"):
                error_desc = "Default parameter file invalid"
            case bytes.fromhex("47"):
                error_desc = "Modbus connection with master control"
            case _:
                error_desc = "Unknown error"

        return DriveError(self.error_code, error_desc)

    async def stop(self):
        self.reg_control.halt_active = True
        await asyncio.sleep(0.2)

    async def resume(self):
        self.reg_control.halt_active = False
        await asyncio.sleep(0.2)

    def worker(self):
        logging.debug("Worker started")
        while not self.terminated:
            logging.debug("Writing registers...")
            self.reg_write()
            self.reg_read()
            self.read_exception()  # TODO Only if error?
            time.sleep(0.1)
        logging.debug("Worker exiting...")
