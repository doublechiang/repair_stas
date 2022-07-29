import os
from re import sub
import shutil
import subprocess
import time
import sys



def upload_bios(ip, biosfile):
    # bios name must be 'bios'
    shutil.copy(biosfile, 'bios')
    cmd = 'sshpass -p "admin" sftp -o StrictHostKeyChecking=no admin@{0}:/var/wcs/home/  <<< $\'put bios\''.format(ip)
    print(cmd)
    os.system(cmd)


    # trigger bios update
    cmd = 'ipmitool -H {0} -U admin -P admin raw 0x38 0x84 0x21 0x00 0x01 0x62 0x69 0x6f 0x73 0x0 0x0 0x0 0x0 0x0 0x0 0x0 0x0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0'.format(ip)
    os.system(cmd)
    # Check update progress
    cmd = 'ipmitool -H {0} -U admin -P admin raw 0x38 0x84 0x21 0x1 0x3'.format(ip)
    while True:
        result=subprocess.run(cmd.split(), stdout=subprocess.PIPE).stdout
        output=result.decode().strip()
        if '04' in output:
            print('Update BIOS done')
            break
        if '03' in output:
            print("03: Updating in progress")
        time.sleep(5)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage {} [BMC_IP] [biosfn]".format(sys.argv[0]))
        exit(1)

    bmc_ip = sys.argv[1]
    upload_bios(sys.argv[1], sys.argv[2])
