#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template, url_for, send_file
from isc_dhcp_leases import Lease, IscDhcpLeases
import logging
import os
import urllib
from urllib.parse import urlencode
import base64
from uut import Uut
from switch import Switch
import settings
from timeit import default_timer as timer
import time

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = 'repair_stas'
logging.basicConfig(level=logging.DEBUG)


@app.route('/upg_bios')
def upg_bios():
    bmc_ip = request.args.get('bmc_ip')
    cmd = f"python3 oob_upg_bios.py {bmc_ip} C2190.BS.3A22.CAP"

    cmd_encode = urllib.parse.quote(cmd.encode())

    webssh = settings.webssh['host']
    base_url = webssh

    params = dict(username='webssh', 
        password=base64.b64encode('webssh'.encode()).decode('utf-8'),
        hostname=settings.hostname,
        command = cmd_encode)
    redirect_url = base_url + '?' + urlencode(params)
    return redirect(redirect_url)



@app.route('/', methods=['get', 'post'])
def home():

    if ((time.time()-os.path.getctime('data/repair.html'))<settings.refresh_limit_time):
        return send_file('data/repair.html')    
    else:
        error = None
        uut_list = []
        lease_file = settings.lease_file
        if os.path.exists(lease_file):
            leases = IscDhcpLeases(lease_file)
        else:
            lease_file = os.path.basename(lease_file)
            leases = IscDhcpLeases(f'./{lease_file}')
        if leases is not None:

            mac_port_list = Switch.getMgmtMacTable(settings.mgmt_switch)
    

    
            cur = leases.get_current()

            # sort the list value by start date
            cur_list = list(cur.values())
            cur_list.sort(key=lambda x:x.start, reverse=True)
            thread_pool = []

            # for mac, port in mac_port_list:
            #     if port > QSFP_PORT_START_INDEX located in switch.py:
            #         continue
            """ Query all the current lease"""
            for s in cur.values():
                u = Uut(s)
                u.start()
                thread_pool.append(u)

            for u in thread_pool:
                u.join()
                if u.bmc_active:
                    if type(mac_port_list) is list:
                        # get LY9 port number
                        for i in mac_port_list:
                            if u.lease.ethernet == i.mac:
                                u.port = i.port
                    uut_list.append(u)

        else:
            error = f'Can not locate lease file at {lease_file}'

        html = (render_template('status.html', cur_list=uut_list, error=error))
        with open("data/repair.html","w") as f:
                f.write(html)
        return render_template('status.html', cur_list=uut_list, error=error)


