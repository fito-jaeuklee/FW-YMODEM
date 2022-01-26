import os
import sys
import time
import random
import serial
from YModem import YModem
from tkinter import filedialog
from cell_on_off_control import Scanning

if __name__ == '__main__':
    cell_ctr = Scanning()
    FIRMWARE_DIRECTORY = filedialog.askopenfilename()
    print("STM MCU firmware directory = ", FIRMWARE_DIRECTORY)

    try:
        for i in range(1, 37):
            cell_com_port = cell_ctr.main(i)

            serial_io = serial.Serial()
            serial_io.port = cell_com_port
            serial_io.baudrate = "115200"
            serial_io.parity = "N"
            serial_io.bytesize = 8
            serial_io.stopbits = 1
            serial_io.timeout = 2

            print("#3")
            try:
                serial_io.open()
            except Exception as e:
                raise Exception("Failed to open serial port!")

            def sender_getc(size):
                return serial_io.read(size) or None

            def sender_putc(data, timeout=15):
                return serial_io.write(data)

            # TODO: Ymodem protocol for flash mode / replace mode

            sender = YModem(sender_getc, sender_putc)
            os.chdir(sys.path[0])
            # file_path = os.path.abspath('test_send_data/fw2.bin')
            sent = sender.send_file(FIRMWARE_DIRECTORY)
            print("FW update done close cell port")
            serial_io.close()
    except:
        print("error close window")
        time.sleep(5)