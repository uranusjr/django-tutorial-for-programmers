import os

bind = '127.0.0.1:8080'
worders = (os.sysconf('SC_NPROCESSORS_ONLN') * 2) + 1
loglevel = 'error'
command = '/project/venv/lunch/bin/gunicorn'
pythonpath = '/project/lunch'
