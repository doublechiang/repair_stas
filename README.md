# Repaire Stations

This App read the dhcpd lease files. Show the non-expired leased lease.
Probe the leased IP with BMC credential and the integrate it with webssh with SOL console.

# Development
$ export FLASK_APP=app.py (app.py is the default app, so it's not required to set this command.)
$ export FLASK_ENV=development
$ python3 -m flask run

# Deployment
## Deployment to Centos with Apache

$yum install python3-mod_wsgi
