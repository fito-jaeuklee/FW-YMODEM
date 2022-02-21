import serial
import serial.tools.list_ports
import codecs
import time

CELL_INIT = "43 45 4C 4C 5F 45 4E 5F 49 4E 49 54 0D 0A"
ONE_CELL_ON_CONFIG = "43 45 4C 4C 5F 53 45 4C 0D 0A"
# ONE_CELL_ON = "43 45 4C 4C %s 5F 4F 4E 5C 72 5C 6E 0D 0A"
ONE_CELL_ON = "43 45 4C 4C %s 5F 4F 4E 0D 0A"
CELL_INIT_COMMAND = "43 45 4C 4C 5F 45 4E 5F 49 4E 49 54 0D 0A"
SYSCOMMAND_HW_INFORMATION = "AC C0 01 10 7D"
SYSCOMMAND_HW_INFORMATION_RESP_SIZE = 23
CELL_OFF = "43 45 4C 4C 5F 4F 46 46 0D 0A 0D 0A 0D 0A"
ENTER_CELL_BL_MODE = "AC C0 01 F4 99"
ENTER_CELL_BL_MODE_RESP_SIZE = 6


class Scanning:
    def __init__(self):
        self.cell_position_serial_num_list_dict = []

    def get_hub_com_port(self, target_vendor_id):
        hub_port_name = ''
        for port in serial.tools.list_ports.comports():
            if port.vid == target_vendor_id:
                hub_port_name = port.device
        if hub_port_name == '':
            print("Please make sure USB port is plug in.")
            raise Exception("Dock USB Port Not Found.")

        return hub_port_name

    def transmit_command_to_hub_mcu(self, hub_mcu_port, command, response_check_string):
        read_byte = 0
        # print(response_check_string)
        if "INITIAL" in response_check_string:
            # print("1")
            read_byte = 32
        elif "OK!" in response_check_string:
            # print("2")
            read_byte = 32
        elif "ACT" in response_check_string:
            # print("3")
            read_byte = 32
        else:
            read_byte = 0

        with serial.Serial(hub_mcu_port, 115200, timeout=0.1) as hub_mcu_uart:
        # while True:
        #     print("check1")
            data_stop = bytes.fromhex(command)
            hub_mcu_uart.write(data_stop)
            read_stop_response = hub_mcu_uart.read(read_byte)
            # print("response = ", read_stop_response)
            # if response_check_string in str(read_stop_response):
            #     return True
            # else:
            #     print("Not return right response")
            time.sleep(1)
        return read_stop_response

    def get_cell_com_port(self, cell_vendor_id):
        cell_port_name = ''
        cell_port_list = []
        for port in serial.tools.list_ports.comports():
            if port.vid == cell_vendor_id:
                cell_port_name = port.device
                cell_port_list.append(cell_port_name)
                # print(cell_port_name)
        if cell_port_name == '':
            print("Please make sure Cell plug into docking")

        return cell_port_list

    # def set_each_cell_on_config(self, hub_port):
    #     with serial.Serial(hub_port, 115200, timeout=0.1) as hub_mcu_uart:
    #         cell_select_config = bytes.fromhex(ONE_CELL_ON_CONFIG)
    #         hub_mcu_uart.write(cell_select_config)
    #         in_bin = hub_mcu_uart.read(64)
    #         print(in_bin)

    def cell_num_com_open(self, hub_port, number, response_check_string):
        hex = codecs.encode(b"%i" % number, "hex")
        command = ONE_CELL_ON % hex.decode("utf8")

        # hub_mcu_uart = serial.Serial(hub_port, 115200)
        with serial.Serial(hub_port, 115200, timeout=0.1) as hub_mcu_uart:

            # cell_on = bytes.fromhex(command)
            # hub_mcu_uart.write(cell_on)
            # in_bin = hub_mcu_uart.read(8)
            # print(in_bin)
            # # return open result here
            #
            # hub_mcu_uart.flushInput()
            # hub_mcu_uart.flushOutput()

            while True:
                # print("check1123")
                cell_on = bytes.fromhex(command)
                hub_mcu_uart.write(cell_on)
                read_stop_response = hub_mcu_uart.read(64)
                if response_check_string in str(read_stop_response):
                    dummy = 1
                    return True
                else:
                    print("Not return right response")
                time.sleep(1)

    def hex_to_ascii(self, hex_name):
        bytes_object = bytes.fromhex(hex_name)
        ascii_name = bytes_object.decode("ASCII")
        return ascii_name

    def get_hw_info(self, usart):
        # print("get hw info")
        retry_cnt = 0
        hex_buf = bytes.fromhex(SYSCOMMAND_HW_INFORMATION)
        while retry_cnt < 3:
            # try:
            # print("try here")
            usart.write(hex_buf)
            in_bin = usart.read(SYSCOMMAND_HW_INFORMATION_RESP_SIZE)
            # print("Print length of in_bin", len(in_bin))
            if len(in_bin) != SYSCOMMAND_HW_INFORMATION_RESP_SIZE:
                # print("Retry hw info")
                usart.write(hex_buf)
                in_bin = usart.read(SYSCOMMAND_HW_INFORMATION_RESP_SIZE)
                retry_cnt += 1
            else:
                # print("Get cell hw info")
                break
            # except usart.SerialTimeoutException:
            #     print("Didn't get any information from cell")
            #     retry_cnt += 1
        in_hex = hex(int.from_bytes(in_bin, byteorder='big'))

        # print("Printed all hw info : ", in_hex)

        serial_number = int(in_hex[10:14], 16)
        # firm_ver = str(int(in_hex[14:18], 16))
        major_firm_ver = str(int(in_hex[14:16], 16))
        minor_firm_ver = str(int(in_hex[16:18], 16))
        product_id = in_hex[18:22]
        version_id = in_hex[22:26]
        product_version = in_hex[30:34]

        product_id_ascii_string = self.hex_to_ascii(product_id)
        version_id_ascii_string = self.hex_to_ascii(version_id)
        product_version_ascii_string = self.hex_to_ascii(product_version)

        serial_number = str(serial_number)
        firm_ver = str(major_firm_ver) + "." + str(minor_firm_ver)

        return product_id_ascii_string, version_id_ascii_string, product_version_ascii_string, serial_number, firm_ver

    def read_hw_info(self, cell_port):
        # self.cell_df = pd.DataFrame()
        try:
            usart = serial.Serial(cell_port, 115200, timeout=3)
        except (OSError, serial.SerialException):
            # print("THIS cell port not read cell info", cell_port)
            return None

        # sum_data, gps_page_size, imu_page_size = cell_info.check_cell_has_data(usart)

        product_id, version_id, product_version, production_number, firm_ver = self.get_hw_info(usart)
        serial_number = "{}{}-{}-{}".format(product_id, version_id, product_version, production_number)
        # print(serial_number)

        return serial_number

    def main(self, open_cell_num_position):
        dummy = 0
        # print(cell_num_com_open(3))
        # print("check", queue)
        try:
            hub_com_port = self.get_hub_com_port(1160)
        except Exception as e:
            raise Exception("Dock USB Port Not Found")

        res = self.transmit_command_to_hub_mcu(hub_com_port, CELL_INIT_COMMAND, "INITIAL OK!")

        if "INITIAL OK!" in str(res):
            dummy = 1
        else:
            print("Dock init fail")

        time.sleep(2)

        # print("Each cell on configuration")

        res = self.transmit_command_to_hub_mcu(hub_com_port, ONE_CELL_ON_CONFIG, "OK!")

        if "OK!" in str(res):
            dummy = 1
        else:
            print("Dock select config fail")

        time.sleep(1)

        # for i in range(1, 3):
        if self.cell_num_com_open(hub_com_port, open_cell_num_position, "ACT OK!"):
            dummy = 1
        else:
            print("Cell com open fail")

        time.sleep(8)

        try:
            cell_com_port = self.get_cell_com_port(1155)[0]
        except:
            cell_serial_num = None
            # print("Not found cell port")
            pass

        time.sleep(1)

        with serial.Serial(cell_com_port, 115200, timeout=0.1) as cell_port:
            # print("check1")
            bl_mode = bytes.fromhex(ENTER_CELL_BL_MODE)
            cell_port.write(bl_mode)
            read_stop_response = cell_port.read(6)
            # print("response = ", read_stop_response)
            # if response_check_string in str(read_stop_response):
            #     return True
            # else:
            #     print("Not return right response")

        time.sleep(1)

        res = self.transmit_command_to_hub_mcu(hub_com_port, CELL_OFF, "OK!")

        if "OK!" in str(res):
            dummy = 1
        else:
            print("Cell OFF fail")

        time.sleep(3)

        if self.cell_num_com_open(hub_com_port, open_cell_num_position, "ACT OK!"):
            dummy = 1
        else:
            print("Cell com open fail")

        time.sleep(8)

        try:
            cell_com_port = self.get_cell_com_port(1155)[0]
            # print(cell_com_port)
            # TODO :change below lines, just return cell com port
            # and FW update will be execute in sender.py main function
            # cell_serial_num = self.read_hw_info(cell_com_port)
            #
            # return cell_com_port
        except:
            cell_serial_num = None
            print("Not found cell port")
            pass

        return cell_com_port




