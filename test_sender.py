import os
import sys
import time
import serial
from YModem import YModem
import glob
from cell_on_off_control import Scanning
import datetime

global global_path


def make_new_log_file(file_path):
    now = datetime.datetime.now()
    log_file = open(file_path + "/" + "%s_ymodem.log" % now.strftime('%Y_%m_%d_%H_%M'), "w+")
    print(log_file.name)

    return log_file


def callback_making_log_file_name(log_file_path):
    global global_path
    global_path = log_file_path
    print("123128747y125835h", global_path)
    # return global_path


def time_header():
    now = datetime.datetime.now()
    return now.strftime("%Y_%m_%d_%H_%M_%S ")


def write_log(msg):
    global global_path
    try:
        file_object = open(global_path, 'a')
        file_object.write(
            str(time_header()) + msg + "\r\n")
        file_object.close()
    except:
        pass


if __name__ == '__main__':
    bin_fw_name = "Cell_X4_V4.6.binary"

    if getattr(sys, 'frozen', False):
        program_directory = os.path.dirname(os.path.abspath(sys.executable))
    else:
        program_directory = os.path.dirname(os.path.abspath(__file__))

    print(program_directory)

    fw_success_device_num = 0
    fw_fail_device_num = 0

    log_file = make_new_log_file(program_directory)
    callback_making_log_file_name(log_file.name)

    save_current_cell_position = 0
    cell_ctr = Scanning()
    # FIRMWARE_DIRECTORY = filedialog.askopenfilename()


    # bin_file_path = glob.glob("*4.6*")
    # print(os.path.abspath("./Cell_X4_V4.6.binary"))
    # print(os.path.dirname("./Cell_X4_V4.6.binary"))
    # print(bin_file_path)
    abs_path = program_directory + "/" + bin_fw_name
    print(abs_path)

    print("STM MCU firmware directory = ", abs_path)
    write_log("STM MCU firmware directory = " + abs_path)

    for i in range(1, 37):
        save_current_cell_position = i
        print("\n  ======== Start cell %d update ! ========" % save_current_cell_position)
        write_log("======== Start cell %d update ! ========" % save_current_cell_position)
        print("         Waiting for update ....             ")
        write_log("         Waiting for update ....             ")
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
            write_log("           Downloading....        ")
            sent = sender.send_file(abs_path)

            print(" ======== Cell %d FW update DONE!  ======== \n" % save_current_cell_position)
            write_log(" ======== Cell %d FW update DONE!  ======== \n" % save_current_cell_position)
            fw_success_device_num = fw_success_device_num + 1
            serial_io.close()
        except Exception as e:
            print(e)
            if "USB" in str(e):
                write_log("Dock usb not connected ! ")
                sys.exit(1)
            print("Fail Cell number = ", save_current_cell_position)
            write_log("Fail Cell number = " + str(save_current_cell_position))
            fw_fail_device_num = fw_fail_device_num + 1

            print("")
            time.sleep(5)
            pass

    print("All process done !")
    write_log("All process done !")
    print("Total = 36 / success = %d / fail = %d" % (fw_success_device_num, fw_fail_device_num))
    write_log("Total = 36 / success = %d / fail = %d" % (fw_success_device_num, fw_fail_device_num))