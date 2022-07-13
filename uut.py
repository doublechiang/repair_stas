from isc_dhcp_leases import Lease, IscDhcpLeases
import subprocess
import urllib.parse
import logging

import settings

class Uut:
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
        cmd = f'ipmitool -H {self.bmc.ip} -U {Uut.user} -P {Uut.passwd} -I lanplus sol activate'
        return urllib.parse.quote(cmd.encode())

    def getWebSolUser(self):
        return 'webssh'
    
    def getWebSolPassBase64(self):
        # based64 coded from webssh
        return 'd2Vic3No'

    def __init_chassis_sn(self):
        cmd = f'ipmitool -H {self.bmc.ip} -U {Uut.user} -P {Uut.passwd} fru print'
        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
        for l in result.splitlines():
            info = l.strip().split(':')
            if info[0].strip() == 'Chassis Serial':
                return (info[1].strip())

    def __init__(self, lease):
        """ Initialize the UUT from the lease file 
        """
        self.bmc = None
        logging.debug(lease)
        if lease.sets.get('vendor-string') == 'udhcp 1.21.1':
            self.bmc = lease
            self.sn = self.__init_chassis_sn()


