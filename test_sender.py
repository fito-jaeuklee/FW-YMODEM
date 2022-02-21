import os
import sys
import time
import serial
from YModem import YModem
# from tkinter import filedialog
import glob
from cell_on_off_control import Scanning

if __name__ == '__main__':
    save_current_cell_position = 0
    cell_ctr = Scanning()
    # FIRMWARE_DIRECTORY = filedialog.askopenfilename()
    bin_file_path = glob.glob(f"./*4.6*")
    abs_path = os.path.abspath(bin_file_path[0][2:])
    print(abs_path)

    print("STM MCU firmware directory = ", abs_path)

    for i in range(1, 37):
        save_current_cell_position = i
        print("\n  ======== Start cell %d update ! ========" % save_current_cell_position)
        print("         Waiting for update ....             ")
        try:
            cell_com_port = cell_ctr.main(i)

            serial_io = serial.Serial()
            serial_io.port = cell_com_port
            serial_io.baudrate = "115200"
            serial_io.parity = "N"
            serial_io.bytesize = 8
            serial_io.stopbits = 1
            serial_io.timeout = 2

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

            print("           Downloading....        ")
            sent = sender.send_file(abs_path)

            print(" ======== Cell %d FW update DONE!  ======== \n" % save_current_cell_position)
            serial_io.close()
        except:
            print("Fail Cell number = ", save_current_cell_position)
            print("")
            time.sleep(5)
            pass