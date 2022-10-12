import logging
import subprocess
import telnetlib
import logging
from telnetlib import Telnet
from collections import namedtuple
# from tkinter import SW


class Switch:
    TIME_OUT = 2
    QSFP_PORT_START_INDEX=49

    @classmethod
    def getMgmtMacTable(cls, ip_list):
        """ A list contian switch mangement port IP
            return the mac address and port number of swithport
        """
        mgmt = list(map(Switch, ip_list))
        mac_tables = []
        for s in mgmt:
            mac_table = s.getMacTable()
            if type(mac_table) is list:
                mac_tables.extend(mac_table)

        return mac_tables



    def getMacTable(self):
        """ Return MAC table format as named tuple or the Exception 
        """
        mac_table = []
        MacTable = namedtuple('MacTable', 'mac port')

        try:
            with Telnet(self.ip) as tn:
                    tn.read_until(b"User:", Switch.TIME_OUT)
                    tn.write("admin".encode('ascii') + b"\n")
                    tn.read_until(b"Password:", Switch.TIME_OUT)
                    tn.write(b"\n")
                    tn.read_until(b"#", Switch.TIME_OUT)
                    tn.write("show mac-addr-table vlan 1".encode('ascii') + b"\n")
                    result = tn.read_until(b"#", Switch.TIME_OUT)
                    tn.write("quit".encode('ascii') + b"\n")
                    tn.read_until(b'(y/n)', Switch.TIME_OUT)
                    tn.write("n".encode('ascii') + b"\n")
                    content = result.decode('utf-8').splitlines()
                    for line in content:
                        line_list = line.split()
                        if len(line_list) == 3 and line_list[2] == 'Learned':
                            mac = line_list[0].lower()
                            port = int(line_list[1].split('/')[1])
                            if port >= self.QSFP_PORT_START_INDEX:
                                continue
                            mac_table.append(MacTable(mac, port))
                    # logging.debug(f"switch: {self.ip}, mac_table: {mac_table}")
        except Exception as error:
            logging.error(error)
            return error
            
        return mac_table

    def __init__(self, ip=None):
        self.ip = ip

if __name__ == '__main__':
    mac_table=Switch.getMgmtMacTable('10.16.0.2 10.16.0.5'.split())
