cd webserver
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
history|tail -50
ls -ltra
python -m pip install --upgrade pymodbus
pip install -r requirements.txt 
git commit -a
pip freeze>feeeze.now
# deploy database
python manage.py
chmod 777 run
# start flask webserver app
./run
# or use a VScode with  #code . # using python flask debug launch configuration on python interpreter in the venv :)