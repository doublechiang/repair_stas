""" All module are singleton
    To use: # import settings
"""

hostname = '192.168.66.53'

lease_file = '/var/lib/dhcpd/dhcpd.leases'

webssh = { 'host' : 'http://{}:8888'.format(hostname) }

gi = '10.16.0.2 10.16.0.5'.split()





