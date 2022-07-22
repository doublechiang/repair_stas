import subprocess
import telnetlib
from telnetlib import Telnet


class Switch:

    def getMacTable(self):
        mac_table = []

        with Telnet(self.ip) as tn:
            tn.read_until(b"User:")
            tn.write("admin".encode('ascii') + b"\n")
            tn.read_until(b"Password:")
            tn.write(b"\n")
            tn.read_until(b"#")
            tn.write("show mac-addr-table vlan 1".encode('ascii') + b"\n")
            result = tn.read_until(b"#")
            tn.write("quit".encode('ascii') + b"\n")
            tn.read_until(b'(y/n)')
            tn.write("n".encode('ascii') + b"\n")
            content = result.decode('utf-8').splitlines()
            for line in content:
                line_list = line.split()
                if len(line_list) == 3 and line_list[2] == 'Learned':
                    mac = line_list[0].lower()
                    port = int(line_list[1].split('/')[1])
                    mac_table.append((mac, port))
            
            return mac_table

    def setip(self, ip):
        self.ip = ip
    def __init__(self):
        pass

if __name__ == '__main__':
    s = Switch()
    s.setip('10.16.2.48')
    out = s.getMacTable()
