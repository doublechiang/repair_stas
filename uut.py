from isc_dhcp_leases import Lease, IscDhcpLeases
import subprocess
import urllib.parse
import logging
import threading

import settings

class Uut(threading.Thread):
    user = 'admin'
    passwd = 'admin'


    def getSolCmd(self):
        pass

    def getWebSshLink(self):
        pass

    def getWebSSHService(self):
        return settings.webssh['host']

    def getWebSolHost(self):
        parsed = urllib.parse.urlparse(settings.webssh['host'])
        netloc = parsed.netloc
        if ':' in netloc:
            # get the part before ':'
            netloc = netloc.split(':', 1)[0]
        return netloc

    def getWebSshSolTitle(self):
        return self.sn

    def getWebSolCmdUrlEncoded(self):
        cmd = f'ipmitool -H {self.lease.ip} -U {Uut.user} -P {Uut.passwd} -I lanplus sol activate'
        return urllib.parse.quote(cmd.encode())

    def getWebSolUser(self):
        return 'webssh'
    
    def getWebSolPassBase64(self):
        # based64 coded from webssh
        return 'd2Vic3No'

    def __init_chassis_sn(self):
        cmd = f'ipmitool -H {self.lease.ip} -U {Uut.user} -P {Uut.passwd} fru print'
        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
        for l in result.splitlines():
            info = l.strip().split(':')
            if info[0].strip() == 'Chassis Serial':
                return (info[1].strip())

    def run(self):
        """ """
        if self.lease is not None:
            cmd = f'ipmitool -H {self.lease.ip} -U {Uut.user} -P {Uut.passwd} fru print'
            try:
                result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
                if result.returncode != 0:
                    raise Exception('fru print return non-zero')

                output = result.stdout.decode('utf-8')
                
                for l in output.splitlines():
                    info = l.strip().split(':')
                    if info[0].strip() == 'Chassis Serial':
                        self.sn= (info[1].strip())
                    if info[0].strip() == 'Board Serial':
                        self.bsn= (info[1].strip())
                    if info[0].strip() == 'Product Serial':
                        self.psn= (info[1].strip())
                self.bmc_active = True
                logging.debug(f'fru print command works on ip:{self.lease.ip}')
            except:
                logging.debug(f'fru print command is not work ip:{self.lease.ip}')

    def __init__(self, lease):
        """ Initialize the UUT from the lease file 
        """
        super(Uut, self).__init__()
        logging.debug(lease)
        self.lease = None
        self.sn = None
        self.bsn = None
        self.psn = None
        self.port = None
        self.bmc_active = False

        if lease is not None:
            if lease.sets is not None:
                vendor_str = lease.sets.get('vendor-string')
                if vendor_str is not None:
                    if 'udhcp' in vendor_str:
                        self.lease = lease

