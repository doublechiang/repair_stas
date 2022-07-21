#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template, url_for
from isc_dhcp_leases import Lease, IscDhcpLeases
import logging
import os

from uut import Uut


app = Flask(__name__)
app.config['APPLICATION_ROOT'] = 'repair_stas'
logging.basicConfig(level=logging.DEBUG)

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
        cur = leases.get_current()
        # sort the list value by start date
        cur_list = list(cur.values())
        cur_list.sort(key=lambda x:x.start, reverse=True)
        thread_pool = []
        for l in cur_list:
            u = Uut(l)
            u.start()
            thread_pool.append(u)

        for u in thread_pool:
            u.join()
            if u.bmc is not None:
                uut_list.append(u)

        
    else:
        error = f'Can not locate lease file at {lease_file}'
    return render_template('status.html', cur_list=uut_list, error=error)


