# """ All module are singleton
#     To use: # import settings
# """


""" All module are singleton
    To use: # import settings
"""
refresh_limit_time = 30
lease_file = '/var/lib/dhcp/dhcpd.leases'
hostname = '192.168.204.169'
webssh = {'host' : f'http://{hostname}:8888'}



mgmt_switch = [
        ['10.16.0.7','SSH',{99 : 'Example'},''],
        ['10.16.0.2','TN',{99 : 'Example'}, ''],
        ['10.16.0.8','SSH',{99 :'Example'},'']
        ]




