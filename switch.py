import logging
import subprocess
import telnetlib
import logging
from telnetlib import Telnet


class Switch:
    TIME_OUT = 2

    def getMacTable(self):
        mac_table = []

        with Telnet(self.ip) as tn:
            try:
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
                        mac_table.append((mac, port))
            except:
                logging.error(f"Telnet IO error")
            
            return mac_table

    def setip(self, ip):
        self.ip = ip
    def __init__(self):
        pass

if __name__ == '__main__':
    s = Switch()
    s.setip('10.16.2.48')
    print(s.getMacTable())
