from pymodbus.client import ModbusTcpClient
import sys

def rback():
    result = client.read_holding_registers(0x0, 0x4)

    if result.isError():
        print("Modbus error!")
        sys.exit(2)
    else:
        print(result.registers)
        print(format(result.registers[0], '0{}_b'.format(8 * 8)))

client = ModbusTcpClient('192.168.2.23')
client.connect()

rback()

result = client.write_registers(0x0, [0x0000, 0x0100, 0x0000, 0x0000])
if result.isError():
    print("Modbus error!")
    sys.exit(2)

rback()

result = client.write_registers(0x0, [0x0100, 0x0100, 0x0000, 0x0000])
if result.isError():
    print("Modbus error!")
    sys.exit(2)

rback()

result = client.write_registers(0x0, [0x0300, 0x0100, 0x0000, 0x0000]) # Assert CCON.STOP
if result.isError():
    print("Modbus error!")
    sys.exit(2)

result = client.write_registers(0x0, [0x0301, 0x0100, 0x0000, 0x0000]) # Assert CPOS.HALT
if result.isError():
    print("Modbus error!")
    sys.exit(2)

# Homing
result = client.write_registers(0x0, [0x0305, 0x0100, 0x0000, 0x0000]) # Assert CPOS.HOM
if result.isError():
    print("Modbus error!")
    sys.exit(2)
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
