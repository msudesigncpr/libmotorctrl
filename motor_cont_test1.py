from pymodbus.client import ModbusTcpClient
import sys
import logging
import threading
import time


class Drive:
    def __init__(self, name, ip_addr):
        self.name = name
        self.ip_addr = ip_addr
        self.client = ModbusTcpClient(ip_addr)
        self.terminated = False
        self.register_out = [0x0000, 0x0000, 0x0000, 0x0000]
        self.reg_status = {"motion_complete": False}

        self.client.connect()
        logging.info("%s : Client is connected!", name)

        logging.info("%s : Initializing write thread...", name)
        self.write_worker = threading.Thread(target=self.worker)
        logging.info("%s : Starting write thread...", name)
        self.write_worker.start()

    def terminate(self):
        self.terminated = True
        self.write_worker.join()
        self.client.close()

    def reg_read(self):
        result = self.client.read_holding_registers(0x0, 0x4)

        if result.isError():
            logging.error("%s : Modbus error!", self.name)
            sys.exit(2)
        else:
            print(result.registers)
            self.reg_status["motion_complete"] = (result.registers[0] & 0x4) == 0x4
            print("Motion complete:", self.reg_status["motion_complete"])

    def reg_write(self, register_out):
        result = self.client.write_registers(0x0, register_out)
        if result.isError():
            print("Modbus error!")
            sys.exit(2)

        self.reg_read()
        time.sleep(0.1)

    def worker(self):
        logging.info("%s : Started", self.name)
        while not self.terminated:
            logging.info("%s : Writing...", self.name)
            self.reg_write(self.register_out)
            self.reg_read()
            time.sleep(0.1)
        logging.info("%s : Exiting", self.name)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    print("Main: Spawning z-axis control...")
    drive_c = Drive("Z", "192.168.2.23")

    print("Clearing registers...")
    drive_c.register_out = [0x0000, 0x0100, 0x0000, 0x0000]
    time.sleep(0.2)

    print("Enabling drive...")
    drive_c.register_out = [0x0100, 0x0100, 0x0000, 0x0000]  # Assert CCON.ENABLED
    time.sleep(0.2)

    print("Disabling stop...")
    drive_c.register_out = [0x0300, 0x0100, 0x0000, 0x0000]  # Assert CCON.STOP
    time.sleep(0.2)

    print("Disabling halt...")
    drive_c.register_out = [0x0301, 0x0100, 0x0000, 0x0000]  # Assert CPOS.HALT
    time.sleep(0.2)

    print("Disabling brake...")
    drive_c.register_out = [0x0701, 0x0100, 0x0000, 0x0000]  # Assert CCON.BRAKE
    time.sleep(0.2)

    print("Clearing faults...")
    drive_c.register_out = [0x0F01, 0x0100, 0x0000, 0x0000]  # Assert CCON.RESET
    time.sleep(0.2)

    print("De-asserting reset...")
    drive_c.register_out = [0x0701, 0x0100, 0x0000, 0x0000]  # Assert CCON.BRAKE
    time.sleep(0.2)

    drive_c.register_out = [0x0F05, 0x0100, 0x0000, 0x0000]  # Assert CPOS.HOM
    time.sleep(0.2)

    while not drive_c.reg_status["motion_complete"]:
        time.sleep(0.1)
    logging.info("Drive Z homing complete!")

    # while readCurrent & 4 == 0 % while Motion not Complete
    #      readCurrent = read(connection, 'holdingregs', 1, 4) % keep reading
    # end
    # print("HERE")

    # Motion
    # result = client.write_registers(0x0, [0x0301, 0x0100, 0x0000, 0x0000]) # Deassert CPOS.HOM
    # result = client.write_registers(0x0, [0x4301, 0x0064, 0x0000, 0x0000]) # Assert CPOS.OPM1
    # result = client.write_registers(0x0, [0x4301, 0x0064, 0x0000, 0x2710]) # Set target to 10k
    # result = client.write_registers(0x0, [0x4703, 0x0064, 0x0000, 0x2710]) # Start

    # readCurrent = read(connection, 'holdingregs', 1, 4)
    #
    # while readCurrent & 4 == 0 % while Motion not Complete
    #      readCurrent = read(connection, 'holdingregs', 1, 4) % keep reading
    # end
    #
    # write(connection, 'holdingregs', 1, cast([0x4701 0x0064 0x0000 0x0000], "double")) % Deassert CCON.START
    # read(connection, 'holdingregs', 1, 4)

    # client.write_coil(1, True, slave=1)        # set information in device
    # result = client.read_coils(2, 3, slave=1)  # get information from device
    # print(result.bits[0])                      # use information
    drive_c.terminate()  # Disconnect device
