# from curses import keyname
import os
# from os.path import exists
from app import create_app, bcrypt
from flask_migrate import upgrade, migrate, init, stamp
from models import db
from models import User
from models import Setting
from models import Slave_dev
# from sqlalchemy import exists 
app = create_app()
app.app_context().push()
db.create_all()

# migrate database to latest revision
if not os.path.exists("migrations"):
    init( )  # init the migration version database directory in migrations directory
stamp()
migrate()
upgrade()

# add a adminuser
adminuser = User(
  username='openplc1',
  name='adwim',
  email='openplc1@example.com',
  pwd=bcrypt.generate_password_hash('openplc1'),
  pict_file= 'users-icon-64x64.png'
  )

# add Settings list

setting1 = Setting( key = 'Modbus_port',    value='502')
setting2 = Setting( key = 'Dnp3_port',      value='20000')
setting3 = Setting( key = 'Start_run_mode', value='false')
setting4 = Setting( key = 'Slave_polling',  value='100')
setting5 = Setting( key = 'Slave_timeout',  value='1000')
setting6 = Setting( key = 'Enip_port',      value='44818')
setting7 = Setting( key = 'Pstorage_polling', value='disabled')

slave_dev1 = Slave_dev(
        dev_name      = 'Ardu',
        dev_type      = 'RTU',
        slave_id      = 1,
        com_port      = 'COM1',
        baud_rate     = 9600,
        parity        = 'N',
        data_bits     = 8 ,
        stop_bits     = 1,
        ip_address    = '127.0.0.1',
        ip_port       = 502,
        di_start      = 1,
        di_size       = 12,
        coil_start    = 1,
        coil_size     = 12,
        ir_start      = 1,
        ir_size       = 12,
        hr_read_start = 1,
        hr_read_size  = 12,
        hr_write_start= 1,
        hr_write_size = 12,
        pause          =12)



try:
    db.session.merge(adminuser)
    db.session.add_all([setting1, setting2, setting3 , setting4, setting5 , setting6 , setting6 , setting7, slave_dev1 ])
    db.session.commit()

except Exception as e:
    print(e)
    db.session.rollback() # user exist if a integrity error
    #obj = User()

