from isc_dhcp_leases import Lease, IscDhcpLeases
import subprocess

class Uut:
    user = 'admin'
    passwd = 'admin'

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
        print(lease)
        if lease.sets.get('vendor-string') == 'udhcp 1.21.1':
            self.bmc = lease
            self.sn = self.__init_chassis_sn()


