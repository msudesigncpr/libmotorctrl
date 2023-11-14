import threading
from pymodbus.client import ModbusTcpClient
import logging
import time
import sys
from enum import IntEnum


class OpMode(IntEnum):
    RECSELECT = 0b0000
    DIRECTAPP = 0b0001
    RESERVED1 = 0b0010
    RESERVED2 = 0b0011


class SetpointMode(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1


class ControlMode(IntEnum):
    POSITIONING = 0b00
    POWER = 0b01
    SPEED = 0b10
    RESERVED = 0b11


class Drive:
    def __init__(self, name, ip_addr):
        self.name = name
        self.ip_addr = ip_addr
        self.drive_init_event = threading.Event()  # To alert main thread
        self.client = ModbusTcpClient(ip_addr)
        self.terminated = False
        self.reg_control = {
            # CCON
            "drive_enabled": False,
            "operation_enabled": False,
            "brake_active": True,
            "reset": False,
            "fct_blocked": False,
            "operation_mode": OpMode.RECSELECT,
            # CPOS
            "halt_active": True,
            "positioning_start": False,
            "homing_start": False,
            "jog_positive": False,
            "jog_negative": False,
            "teach": False,
            "clear_path": False,
            # CDIR
            "setpoint_mode": SetpointMode.ABSOLUTE,
            "control_mode": ControlMode.POSITIONING,
            "stroke_limit_bypass": False,
            # SP 1
            "preselection": 0,
            # SP 2
            "setpoint": 0,
        }
        self.reg_status = {
            # SCON
            "drive_enabled": False,
            "operation_enabled": False,
            "warning_present": False,
            "fault_present": False,
            "load_applied": False,
            "fct_blocked": False,
            "operation_mode": OpMode.RECSELECT,
            # SPOS
            "halt_active": True,
            "ack_start": False,
            "motion_complete": False,
            "ack_teach": False,
            "is_moving": False,
            "following_error": False,
            "still_monitoring": False,
            "reference_set": False,
            # SDIR
            "setpoint_mode": SetpointMode.ABSOLUTE,
            "control_mode": ControlMode.POSITIONING,
            "speed_limit_reached": False,
            "stroke_limit_reached": False,
            # SP 1
            "preselection": 0,
            # SP 2
            "setpoint": 0,
        }

        self.client.connect()
        logging.info("%s : Client is connected!", name)

        logging.info("%s : Initializing write thread...", name)
        self.write_worker = threading.Thread(target=self.worker)
        logging.info("%s : Starting write thread...", name)
        self.write_worker.start()
        time.sleep(0.2)
        self.initialize()

    def initialize(self):
        time.sleep(0.2)

        logging.info("%s : Enabling drive...", self.name)
        self.reg_control["drive_enabled"] = True
        time.sleep(0.2)

        logging.info("%s : Disabling stop...", self.name)
        self.reg_control["operation_enabled"] = True
        time.sleep(0.2)

        logging.info("%s : Disabling halt...", self.name)
        self.reg_control["halt_active"] = False
        time.sleep(0.2)

        logging.info("%s : Disabling brake...", self.name)
        self.reg_control["brake_active"] = False
        time.sleep(0.2)

        logging.info("%s : Clearing faults...", self.name)
        self.reg_control["reset"] = True
        time.sleep(0.2)

        logging.info("%s : De-asserting reset...", self.name)
        self.reg_control["reset"] = False
        time.sleep(0.2)

        logging.info("%s : Starting homing...", self.name)
        self.reg_control["homing_start"] = True
        time.sleep(0.2)

        while not self.reg_status["motion_complete"]:
            time.sleep(0.1)
        self.reg_control["homing_start"] = False
        logging.info("%s : Drive homing complete!", self.name)

        logging.info("%s : Setting operation mode to direct application...", self.name)
        self.reg_control["operation_mode"] = OpMode.DIRECTAPP
        self.reg_control["preselection"] = 100
        time.sleep(0.2)
        self.drive_init_event.set()

    def terminate(self):
        self.reg_control["drive_enabled"] = False
        self.reg_control["operation_enabled"] = False
        self.reg_control["halt_active"] = True
        time.sleep(0.2)
        self.terminated = True
        time.sleep(0.2)
        self.write_worker.join()
        self.client.close()

    def reg_read(self):
        result = self.client.read_holding_registers(0x0, 0x4)

        if result.isError():
            logging.error("%s : Modbus error!", self.name)
            sys.exit(2)
        else:
            logging.debug("%s : Raw register state is %s", self.name, result.registers)

            # Parse SCON
            self.reg_status["drive_enabled"] = bool(
                ((result.registers[0] >> 0) >> 8) & 1
            )
            self.reg_status["operation_enabled"] = bool(
                ((result.registers[0] >> 1) >> 8) & 1
            )
            self.reg_status["warning_present"] = bool(
                ((result.registers[0] >> 2) >> 8) & 1
            )
            self.reg_status["fault_present"] = bool(
                ((result.registers[0] >> 3) >> 8) & 1
            )
            self.reg_status["load_applied"] = bool(
                ((result.registers[0] >> 4) >> 8) & 1
            )
            self.reg_status["fct_blocked"] = bool(((result.registers[0] >> 5) >> 8) & 1)
            self.reg_status["operation_mode"] = int((result.registers[0] >> 6) >> 8)

            # Parse SPOS
            self.reg_status["halt_active"] = not bool((result.registers[0] >> 0) & 1)
            self.reg_status["ack_start"] = bool((result.registers[0] >> 1) & 1)
            self.reg_status["motion_complete"] = bool((result.registers[0] >> 2) & 1)
            self.reg_status["ack_teach"] = bool((result.registers[0] >> 3) & 1)
            self.reg_status["is_moving"] = bool((result.registers[0] >> 4) & 1)
            self.reg_status["following_error"] = bool((result.registers[0] >> 5) & 1)
            self.reg_status["still_monitoring"] = bool((result.registers[0] >> 6) & 1)
            self.reg_status["reference_set"] = bool((result.registers[0] >> 7) & 1)

            # Parse SDIR
            self.reg_status["setpoint_mode"] = int(
                ((result.registers[1] >> 0) >> 8) & 1
            )
            self.reg_status["control_mode"] = int(
                ((result.registers[1] >> 1) >> 8) & 0b11
            )
            self.reg_status["speed_limit_reached"] = bool(
                ((result.registers[1] >> 4) >> 8) & 1
            )
            self.reg_status["stroke_limit_reached"] = bool(
                ((result.registers[1] >> 5) >> 8) & 1
            )
            # SP 1
            self.reg_status["preselection"] = int(result.registers[1] & 0xFFFF)
            # SP 2
            self.reg_status["setpoint"] = (int(result.registers[2]) << 16) + int(
                result.registers[3]
            )

            logging.debug(
                "%s : Parsed register state is %s", self.name, self.reg_status
            )

    def reg_write(self):
        register_out = [0x0000, 0x0000, 0x0000, 0x0000]

        # CCON
        register_out[0] |= (int(self.reg_control["drive_enabled"]) << 0) << 8
        register_out[0] |= (int(self.reg_control["operation_enabled"]) << 1) << 8
        register_out[0] |= (int(not self.reg_control["brake_active"]) << 2) << 8
        register_out[0] |= (int(self.reg_control["reset"]) << 3) << 8
        register_out[0] |= (int(self.reg_control["fct_blocked"]) << 5) << 8
        register_out[0] |= (int(self.reg_control["operation_mode"]) << 6) << 8

        # CPOS
        register_out[0] |= int(not self.reg_control["halt_active"]) << 0
        register_out[0] |= int(self.reg_control["positioning_start"]) << 1
        register_out[0] |= int(self.reg_control["homing_start"]) << 2
        register_out[0] |= int(self.reg_control["jog_positive"]) << 3
        register_out[0] |= int(self.reg_control["jog_negative"]) << 4
        register_out[0] |= int(self.reg_control["teach"]) << 5
        register_out[0] |= int(self.reg_control["clear_path"]) << 6

        # CDIR
        register_out[1] |= (int(self.reg_control["setpoint_mode"]) << 0) << 8
        register_out[1] |= (int(self.reg_control["control_mode"]) << 1) << 8
        register_out[1] |= (int(self.reg_control["stroke_limit_bypass"]) << 5) << 8

        # SP 1
        register_out[1] |= self.reg_control["preselection"]

        # SP 2
        register_out[2] |= self.reg_control["setpoint"] >> 16
        register_out[3] |= self.reg_control["setpoint"] & 0xFFFF
        logging.debug("%s : Register write: %s", self.name, register_out)

        result = self.client.write_registers(0x0, register_out)
        if result.isError():
            logging.error("%s : Communication error!", self.name)
            sys.exit(2)

        self.reg_read()
        time.sleep(0.1)

    def worker(self):
        logging.info("%s : Worker started", self.name)
        while not self.terminated:
            logging.debug("%s : Writing registers...", self.name)
            self.reg_write()
            self.reg_read()
            time.sleep(0.1)
        logging.info("%s : Worker exiting...", self.name)
