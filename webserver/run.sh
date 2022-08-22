# Win WSL2  port forwarding to hyperV machin 127.18.145.123 e dotn forget host firewall  for app ports
# netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=172.18.145.123
cd ../webserver
. .venv/bin/activate
FLASK_APP=routes.py FLASK_DEBUG=1 FLASK_ENV=development flask run
