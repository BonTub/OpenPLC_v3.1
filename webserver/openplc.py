# Use this for OpenPLC console: http://eyalarubas.com/python-subproc-nonblock.html
import subprocess
import socket
import errno
import time
from threading import Thread

from app import db
from models import Setting
from models import Slave_dev
import os
from os import path, remove

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )


def display_time(seconds, granularity=2):
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append(f"{0} {1}".format(value, name))
    return ', '.join(result[:granularity])


class NonBlockingStreamReader:

    end_of_stream = False
    
    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''

        self._s = stream
        self._q = queue()

        '''
            Collect lines from 'stream' and put them in 'queue'.
        '''
        def _populateQueue(stream, queue):

            #while True:
            while not self.end_of_stream:
                rline = stream.readline()
                if rline:
                    queue.put( rline )
                    if (rline.find("Compilation finished with errors!") >= 0 or rline.find("Compilation finished successfully!") >= 0 ):
                        self.end_of_stream = True
                else:
                    self.end_of_stream = True
                    raise UnexpectedEndOfStream

        self._t = Thread(target = _populateQueue, args = (self._s, self._q))
        self._t.daemon = True
        self._t.start()  # start collecting lines from the stream

    def readline(self, timeout = None):
        try:
            return self._q.get(block = timeout is not None,
                    timeout = timeout)
        except queue.Empty:
            return None

class UnexpectedEndOfStream(Exception): pass

class runtime:
    project_file = ""
    project_name = ""
    project_description = ""
    runtime_status = "Stopped"
    
    def start_runtime(self):
        if (self.status() == "Stopped"):
            self.theprocess = subprocess.Popen(['./core/openplc'])  # XXX: iPAS
            self.runtime_status = "Running"
    
    def stop_runtime(self):
        if (self.status() == "Running"):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 43628))
                s.send('quit()\n')
                data = s.recv(1000)
                s.close()
                self.runtime_status = "Stopped"

                while self.theprocess.poll() is None:  # XXX: iPAS, to prevent the defunct killed process.
                    time.sleep(1)  # https://www.reddit.com/r/learnpython/comments/776r96/defunct_python_process_when_using_subprocesspopen/
                    
            except socket.error as serr:
                print("Failed to stop the runtime. Error: " + str(serr))
    
    def compile_program(self, st_file):
        if (self.status() == "Running"):
            self.stop_runtime()
            
        self.is_compiling = True
        global compilation_status_str
        global compilation_object
        compilation_status_str = ""
        a = subprocess.Popen(['./scripts/compile_program.sh', str(st_file)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        compilation_object = NonBlockingStreamReader(a.stdout)
    
    def compilation_status(self):
        global compilation_status_str
        global compilation_object
        while True:
            line = compilation_object.readline()
            if not line: break
            compilation_status_str += line
        return compilation_status_str
    
    def status(self):
        if ('compilation_object' in globals()):
            if (compilation_object.end_of_stream == False):
                return "Compiling"
        
        #If it is running, make sure that it really is running
        if (self.runtime_status == "Running"):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 43628))
                s.send('exec_time()\n')
                data = s.recv(10000)
                s.close()
                self.runtime_status = "Running"
            except socket.error as serr:
                print("OpenPLC Runtime is not running. Error: " + str(serr))
                self.runtime_status = "Stopped"
        
        return self.runtime_status
    
    def start_modbus(self, port_num):
        if (self.status() == "Running"):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 43628))
                s.send('start_modbus(' + str(port_num) + ')\n')
                data = s.recv(1000)
                s.close()
            except:
                print("Error connecting to OpenPLC runtime")
                
    def stop_modbus(self):
        if (self.status() == "Running"):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 43628))
                s.send('stop_modbus()\n')
                data = s.recv(1000)
                s.close()
            except:
                print("Error connecting to OpenPLC runtime")

    def start_dnp3(self, port_num):
        if (self.status() == "Running"):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 43628))
                s.send('start_dnp3(' + str(port_num) + ')\n')
                data = s.recv(1000)
                s.close()
            except:
                print("Error connecting to OpenPLC runtime")
        
    def stop_dnp3(self):
        if (self.status() == "Running"):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 43628))
                s.send('stop_dnp3()\n')
                data = s.recv(1000)
                s.close()
            except:
                print("Error connecting to OpenPLC runtime")
                
    def start_enip(self, port_num):
        if (self.status() == "Running"):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 43628))
                s.send('start_enip(' + str(port_num) + ')\n')
                data = s.recv(1000)
                s.close()
            except:
                print("Error connecting to OpenPLC runtime")
                
    def stop_enip(self):
        if (self.status() == "Running"):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 43628))
                s.send('stop_enip()\n')
                data = s.recv(1000)
                s.close()
            except:
                print("Error connecting to OpenPLC runtime")
    
    def start_pstorage(self, poll_rate):
        if (self.status() == "Running"):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 43628))
                s.send('start_pstorage(' + str(poll_rate) + ')\n')
                data = s.recv(1000)
                s.close()
            except:
                print("Error connecting to OpenPLC runtime")
                
    def stop_pstorage(self):
        if (self.status() == "Running"):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 43628))
                s.send('stop_pstorage()\n')
                data = s.recv(1000)
                s.close()
            except:
                print("Error connecting to OpenPLC runtime")
    
    def logs(self):
        if (self.status() == "Running"):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 43628))
                s.send('runtime_logs()\n')
                data = s.recv(1000000)
                s.close()
                return data
            except:
                print("Error connecting to OpenPLC runtime")
            
            return "Error connecting to OpenPLC runtime"
        else:
            return "OpenPLC Runtime is not running"
        
    def exec_time(self):
        if (self.status() == "Running"):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', 43628))
                s.send('exec_time()\n')
                data = s.recv(10000)
                s.close()
                return display_time(int(data), 4)
            except:
                print("Error connecting to OpenPLC runtime")
            
            return "Error connecting to OpenPLC runtime"
        else:
            return "N/A"


def configure_runtime(app):
    global openplc_runtime
    with app.app_context():
        session = db.session.session_factory()
        try:
            # a list
            result = session.query(Setting).all()
        except:
            print("db session settings trouble")
            return

        # use the settings    
        for setting in result:
            app.config[setting.key] = setting.value
            # print(setting.key, setting.value)
            if setting.key == "Modbus_port":
                if setting.value != "disabled":
                    print("Enabling Modbus on port " + str(int(setting.value)))
                    openplc_runtime.start_modbus(int(setting.value))
                else:
                    print("Disabling Modbus")
                    openplc_runtime.stop_modbus()
            elif setting.key == "Dnp3_port":
                if setting.value != "disabled":
                    print("Enabling DNP3 on port " + str(int(setting.value)))
                    openplc_runtime.start_dnp3(int(setting.value))
                else:
                    print("Disabling DNP3")
                    openplc_runtime.stop_dnp3()
            elif setting.key == "Enip_port":
                if setting.value != "disabled":
                    print("Enabling Enip on port " + str(int(setting.value)))
                    openplc_runtime.start_enip(int(setting.value))
                else:
                    print("Disabling Enip")
                    openplc_runtime.stop_enip()
            elif setting.key == "Pstorage_polling":
                if setting.value != "disabled":
                    print("Enabling Persistent Storage with polling rate of " + str(int(setting.value)) + " seconds")
                    openplc_runtime.start_pstorage(int(setting.value))
                else:
                    print("Disabling Persistent Storage")
                    openplc_runtime.stop_pstorage()
                    delete_persistent_file()
            else:
                print( setting )
        print( "Default Settings applied app.config written" )
        generate_mbconfig(app)
    return


def delete_persistent_file():
    if (os.path.isfile("persistent.file")):
        os.remove("persistent.file")
    print("persistent.file removed!")

def generate_mbconfig(app):
    global openplc_runtime
    with app.app_context():
        session = db.session.session_factory()
        try:
            # a list
            result = session.query(Slave_dev).count()
            num_devices = int(result)
            mbconfig = 'Num_Devices = "' + str(num_devices) + '"'
            mbconfig += '\nPolling_Period = "' + app.config['Slave_polling'] + '"'
            mbconfig += '\nTimeout = "' + app.config['Slave_timeout'] + '"'

            result = session.query(Slave_dev).all()
               
            device_counter = 0
            for row in result:
                mbconfig += mb_config(row,device_counter)
                device_counter += 1
            # print(mbconfig)
            
        except:
            print("db session modbusconfig trouble")
            return
        # print(app.config['Slave_polling'])
    return


def mb_config(row,device_counter):
    mbconfig = """
# ------------
#   DEVICE """
    mbconfig += str(device_counter)
    mbconfig += """
# ------------
"""
    mbconfig += 'device' + str(device_counter) + '.name = "' + row.dev_name + '"\n'
    mbconfig += 'device' + str(device_counter) + '.slave_id = "' + str(row.slave_id) + '"\n'
    if ((str(row.dev_type) == 'ESP32') or (str(row.dev_type) == 'ESP8266') or (str(row.dev_type) == 'TCP')):
        mbconfig += 'device' + str(device_counter) + '.protocol = "TCP"\n'
        mbconfig += 'device' + str(device_counter) + '.address = "' + str(row.ip_address) + '"\n'
    else:
        mbconfig += 'device' + str(device_counter) + '.protocol = "RTU"\n'
        if str(row.com_port ).startswith("COM"):
            port_name = "/dev/ttyS" + str(int(str(row.com_port).split("COM")[1]) - 1)
        else:
            port_name = str(row.com_port )
    mbconfig += 'device' + str(device_counter) + '.address       = "' + port_name + '"\n'
    mbconfig += 'device' + str(device_counter) + '.IP_Port       = "' + str(row.ip_port) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.RTU_Baud_Rate = "' + str(row.baud_rate) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.RTU_Parity    = "' + str(row.parity) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.RTU_Data_Bits = "' + str(row.data_bits) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.RTU_Stop_Bits = "' + str(row.stop_bits) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.RTU_TX_Pause  = "' + str(row.pause) + '"\n\n'               
    mbconfig += 'device' + str(device_counter) + '.Discrete_Inputs_Start        = "' + str(row.di_start) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.Discrete_Inputs_Size         = "' + str(row.di_size) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.Coils_Start                  = "' + str(row.coil_start) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.Coils_Size                   = "' + str(row.coil_size) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.Input_Registers_Start        = "' + str(row.ir_start) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.Input_Registers_Size         = "' + str(row.ir_size) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.Holding_Registers_Read_Start = "' + str(row.hr_read_start) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.Holding_Registers_Read_Size  = "' + str(row.hr_read_size) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.Holding_Registers_Start      = "' + str(row.hr_write_start) + '"\n'
    mbconfig += 'device' + str(device_counter) + '.Holding_Registers_Size       = "' + str(row.hr_write_size) + '"\n'
    return mbconfig            



'''




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
openplc_runtime = runtime()