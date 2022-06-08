from flask import Flask
from flask import session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import(
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
    )


login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'secret-key'
    # import os
    # from os import urandom
    # app.secret_key = str(os.urandom(16)) # disables the cookied headers from other/previous app instances
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    return app


#def init_app(app):
def configure_openplc(app):
    global openplc_runtime
    with app.app_context():
        pass



    #   for setting in db.session.query("settings").all():
    #       print( setting )
    # ...
''' 
    Settings.query().
    database = "openplc.db"
    conn = create_connection(database)
    if (conn != None):
        try:
            print("Openning database")
            cur = conn.cursor()
            cur.execute("SELECT * FROM Settings")
            rows = cur.fetchall()
            cur.close()
            conn.close()

            for row in rows:
                if (row[0] == "Modbus_port"):
                    if (row[1] != "disabled"):
                        print("Enabling Modbus on port " + str(int(row[1])))
                        openplc_runtime.start_modbus(int(row[1]))
                    else:
                        print("Disabling Modbus")
                        openplc_runtime.stop_modbus()
                elif (row[0] == "Dnp3_port"):
                    if (row[1] != "disabled"):
                        print("Enabling DNP3 on port " + str(int(row[1])))
                        openplc_runtime.start_dnp3(int(row[1]))
                    else:
                        print("Disabling DNP3")
                        openplc_runtime.stop_dnp3()
                elif (row[0] == "Enip_port"):
                    if (row[1] != "disabled"):
                        print("Enabling EtherNet/IP on port " + str(int(row[1])))
                        openplc_runtime.start_enip(int(row[1]))
                    else:
                        print("Disabling EtherNet/IP")
                        openplc_runtime.stop_enip()
                elif (row[0] == "Pstorage_polling"):
                    if (row[1] != "disabled"):
                        print("Enabling Persistent Storage with polling rate of " + str(int(row[1])) + " seconds")
                        openplc_runtime.start_pstorage(int(row[1]))
                    else:
                        print("Disabling Persistent Storage")
                        openplc_runtime.stop_pstorage()
                        delete_persistent_file()
        except Error as e:
            print("error connecting to the database" + str(e))
    else:
        print("Error opening DB")
 '''

'''  
def delete_persistent_file():
    if (os.path.isfile("persistent.file")):
        os.remove("persistent.file")
    print("persistent.file removed!")


def generate_mbconfig():
    database = "openplc.db"
    conn = create_connection(database)
    if (conn != None):
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM Slave_dev")
            row = cur.fetchone()
            num_devices = int(row[0])
            mbconfig = 'Num_Devices = "' + str(num_devices) + '"'
            cur.close()
            
            cur=conn.cursor()
            cur.execute("SELECT * FROM Settings")
            rows = cur.fetchall()
            cur.close()
                    
            for row in rows:
                if (row[0] == "Slave_polling"):
                    slave_polling = str(row[1])
                elif (row[0] == "Slave_timeout"):
                    slave_timeout = str(row[1])
                    
            mbconfig += '\nPolling_Period = "' + slave_polling + '"'
            mbconfig += '\nTimeout = "' + slave_timeout + '"'
            
            cur = conn.cursor()
            cur.execute("SELECT * FROM Slave_dev")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            device_counter = 0
            for row in rows:
                mbconfig += """
# ------------
#   DEVICE """
                mbconfig += str(device_counter)
                mbconfig += """
# ------------
"""
                mbconfig += 'device' + str(device_counter) + '.name = "' + str(row[1]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.slave_id = "' + str(row[3]) + '"\n'
                if (str(row[2]) == 'ESP32' or str(row[2]) == 'ESP8266' or str(row[2]) == 'TCP'):
                    mbconfig += 'device' + str(device_counter) + '.protocol = "TCP"\n'
                    mbconfig += 'device' + str(device_counter) + '.address = "' + str(row[9]) + '"\n'
                else:
                    mbconfig += 'device' + str(device_counter) + '.protocol = "RTU"\n'
                    if (str(row[4]).startswith("COM")):
                        port_name = "/dev/ttyS" + str(int(str(row[4]).split("COM")[1]) - 1)
                    else:
                        port_name = str(row[4])
                    mbconfig += 'device' + str(device_counter) + '.address = "' + port_name + '"\n'
                mbconfig += 'device' + str(device_counter) + '.IP_Port = "' + str(row[10]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.RTU_Baud_Rate = "' + str(row[5]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.RTU_Parity = "' + str(row[6]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.RTU_Data_Bits = "' + str(row[7]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.RTU_Stop_Bits = "' + str(row[8]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.RTU_TX_Pause = "' + str(row[21]) + '"\n\n'
                
                mbconfig += 'device' + str(device_counter) + '.Discrete_Inputs_Start = "' + str(row[11]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.Discrete_Inputs_Size = "' + str(row[12]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.Coils_Start = "' + str(row[13]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.Coils_Size = "' + str(row[14]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.Input_Registers_Start = "' + str(row[15]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.Input_Registers_Size = "' + str(row[16]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.Holding_Registers_Read_Start = "' + str(row[17]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.Holding_Registers_Read_Size = "' + str(row[18]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.Holding_Registers_Start = "' + str(row[19]) + '"\n'
                mbconfig += 'device' + str(device_counter) + '.Holding_Registers_Size = "' + str(row[20]) + '"\n'
                device_counter += 1
                
            with open('./mbconfig.cfg', 'w+') as f: f.write(mbconfig)
            
        except Error as e:
            print("error connecting to the database" + str(e))
    else:
        print("Error opening DB")
                 '''
