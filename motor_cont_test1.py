from pymodbus.client import ModbusTcpClient
import sys
import logging
import threading
import time

DONE = False
register_to_write = [0x0000, 0x0000, 0x0000, 0x0000]

def rback():
    result = client.read_holding_registers(0x0, 0x4)

    if result.isError():
        logging.error("Modbus error!")
        sys.exit(2)
    else:
        print(result.registers)
        # print(format(result.registers[0], '0{}_b'.format(8 * 8)))

def wout(register_out):
    result = client.write_registers(0x0, register_out)
    if result.isError():
        print("Modbus error!")
        sys.exit(2)

    rback()
    time.sleep(0.1)

def worker():
    logging.info("Write : starting")
    while not DONE:
        logging.info("Write : Writing...")
        wout(register_to_write)
        rback()
        time.sleep(0.1)
    logging.info("Write : Exiting")

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")


    client = ModbusTcpClient('192.168.2.23')
    client.connect()
    logging.info("Main : Client is connected!")

    logging.info("Main : Initializing write thread...")
    write_worker = threading.Thread(target=worker)
    logging.info("Main : Starting write thread...")
    write_worker.start()

    print("BLOCK 1")
    register_to_write = [0x0000, 0x0100, 0x0000, 0x0000]
    time.sleep(1)

    print("BLOCK 2")
    register_to_write = [0x0100, 0x0100, 0x0000, 0x0000] # Assert CCON.ENABLED
    time.sleep(1)

    print("BLOCK 3")
    register_to_write = [0x0300, 0x0100, 0x0000, 0x0000] # Assert CCON.STOP
    time.sleep(1)

    print("BLOCK 4")
    register_to_write = [0x0301, 0x0100, 0x0000, 0x0000] # Assert CPOS.HALT
    time.sleep(1)

    print("BLOCK 5")
    register_to_write = [0x0701, 0x0100, 0x0000, 0x0000] # Assert CCON.BRAKE
    time.sleep(1)

    print("BLOCK 6")
    register_to_write = [0x0F01, 0x0100, 0x0000, 0x0000] # Assert CCON.RESET
    time.sleep(1)

    print("BLOCK 7")
    register_to_write = [0x0701, 0x0100, 0x0000, 0x0000] # Assert CCON.BRAKE
    time.sleep(1)

    register_to_write = [0x0F05, 0x0100, 0x0000, 0x0000] # Assert CPOS.HOM
    time.sleep(0.1)

    # TODO Block await homing

    # Homing
    # for i in range(100):
    #     print("BLOCK 8")
    #     wout([0x0F05, 0x0100, 0x0000, 0x0000]) # Assert CPOS.HOM
    #     time.sleep(0.1)
    wait = input("Waiting...")

    # while readCurrent & 4 == 0 % while Motion not Complete
    #      readCurrent = read(connection, 'holdingregs', 1, 4) % keep reading
    # end
    # print("HERE")

    # Motion
    #result = client.write_registers(0x0, [0x0301, 0x0100, 0x0000, 0x0000]) # Deassert CPOS.HOM
    #result = client.write_registers(0x0, [0x4301, 0x0064, 0x0000, 0x0000]) # Assert CPOS.OPM1
    #result = client.write_registers(0x0, [0x4301, 0x0064, 0x0000, 0x2710]) # Set target to 10k
    #result = client.write_registers(0x0, [0x4703, 0x0064, 0x0000, 0x2710]) # Start

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
    client.close()                             # Disconnect device
