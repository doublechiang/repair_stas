import logging
import subprocess
import telnetlib
import logging
import time
import queue 
import paramiko
from telnetlib import Telnet
from collections import namedtuple
from multiprocessing import Lock, Process, Queue, current_process

from timeit import default_timer as timer

SHARED_MAC_TABLES = []

class Switch:
    TIME_OUT = 2
    QSFP_PORT_START_INDEX=45
    RESULTS = Queue()
    

    @classmethod
    def getMgmtMacTable(cls, ip_list):
        """ A list contian switch mangement port IP
            return the mac address and port number of swithport
        """        
        MacTable = namedtuple('MacTable', 'mac port')
        mgmt = list(map(Switch, ip_list))
        mac_tables = []
        temp = Switch()        
        numberOfProcesses = 3
        tasksToDo = Queue()
        results = temp.RESULTS
        processes = []

        for s in mgmt:
            tasksToDo.put(s)
        time.sleep(0.1)

        for w in range(numberOfProcesses):
            p = Process(target=temp.getMacTable, args=(tasksToDo,results))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()
        
        while (not tasksToDo.empty()):
            pass

        while (not results.empty()):
            grab = results.get()
            mac_table = (MacTable(grab[0],grab[1]))           
            mac_tables.append(mac_table)

        return mac_tables

    #Grabs Mac Address Table from a switch with SSH Protocol
    def sshSwitch(self,ip):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip,username='admin', password='qmfremont',port=22)
            conn = client.invoke_shell()
            conn.sendall('show mac-addr-table vlan 1\n')
            conn.sendall('\n')
            time.sleep(1)
            output = ''

            while not output.endswith('#'):
                response = conn.recv(2048).decode('utf-8')
                output += response

            lines = output.split("\n") 
            client.close()
            return lines
        except Exception as error:
                        logging.error(error)
                        return error 

    #Grabs Mac Address Table from a switch with Telnet Protocol
    def telnetSwitch(self,ip):
        try:
            with Telnet(str(ip)) as tn:
                    tn.read_until(b"User:", Switch.TIME_OUT)
                    tn.write("admin".encode('ascii') + b"\n")
                    tn.read_until(b"Password:", Switch.TIME_OUT)
                    tn.write(b"\n")
                    tn.read_until(b"#", Switch.TIME_OUT)
                    tn.write("show mac-addr-table vlan 1".encode('ascii') + b"\n")
                    tn.write(b"\n")
                    result = tn.read_until(b"#", Switch.TIME_OUT)
                    tn.write("quit".encode('ascii') + b"\n")
                    tn.read_until(b'(y/n)', Switch.TIME_OUT)
                    tn.write("n".encode('ascii') + b"\n")
                    content = result.decode('utf-8').splitlines()
                    return content
        except Exception as error:
            logging.error(error)
            return error  



    def getMacTable(self,tasksToDo,sharedMacTable):
        """ Return MAC table format as named tuple or the Exception 
        """
        while True:
            try:
                task = tasksToDo.get_nowait()
            except queue.Empty:
                break
            else:
                mac_table = []
                if (task.type == 'SSH'):
                    lines = self.sshSwitch(task.ip)
                else: 
                    lines = self.telnetSwitch(task.ip)

                for line in lines:
                    line_list = line.split()
                    if len(line_list) == 3 and line_list[2] == 'Learned':
                        mac = line_list[0].lower()
                        port = int(line_list[1].split('/')[1])
                        if port >= task.QSFP_PORT_START_INDEX:
                            continue
                        elif (port not in task.names):
                            self.RESULTS.put([mac,f'{port} {task.area}'])
                        else:
                            self.RESULTS.put([mac,f'{port} {task.names[port]} : {task.area}'])
                       
                return self.RESULTS

    def __init__(self, data=list):
        try:
          self.ip = data[0]
          self.type = data[1]
          self.names = data[2]
          self.area = data[3]
        except:
          pass
if __name__ == '__main__':
    start = timer()
    mac_table=Switch.getMgmtMacTable([
                                    ['10.16.0.7','SSH',{99 :'Example'},''],
                                    ['10.16.0.2','TN',{99 :'Example'},''],
                                    ['10.16.0.8','SSH',{99 :'Example'},'']
                                    ])

    for i in mac_table:
        print (i)
    end = timer()
    print (end-start)
