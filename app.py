#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template, url_for
from isc_dhcp_leases import Lease, IscDhcpLeases
import logging
import os
import urllib
from urllib.parse import urlencode
import base64


from uut import Uut
from switch import Switch
import settings


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
        hostname='192.168.66.53',
        command = cmd_encode)
    redirect_url = base_url + '?' + urlencode(params)
    return redirect(redirect_url)



@app.route('/', methods=['get', 'post'])
def home():
    error = None
    uut_list = []
    lease_file = '/var/lib/dhcpd/dhcpd.leases'
    if os.path.exists(lease_file):
        leases = IscDhcpLeases(lease_file)
    else:
        lease_file = os.path.basename(lease_file)
        leases = IscDhcpLeases(f'./{lease_file}')
    if leases is not None:

        s= Switch()
        s.setip('10.16.2.48')
        mac_port_list = s.getMacTable()
        cur = leases.get_current()
        # sort the list value by start date
        cur_list = list(cur.values())
        cur_list.sort(key=lambda x:x.start, reverse=True)
        thread_pool = []

        for mac, port in mac_port_list:
            if port > 48:
                continue
            lease = cur.get(mac)
            u = Uut(lease)
            u.port = port
            u.start()
            thread_pool.append(u)

        for u in thread_pool:
            u.join()
            if u.bmc is not None:
                uut_list.append(u)

        
    else:
        error = f'Can not locate lease file at {lease_file}'
    return render_template('status.html', cur_list=uut_list, error=error)


