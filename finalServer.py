import time
from flask import Flask ,jsonify ,request
import json
import os
import sys
from flask_cors import CORS
import serial.tools.list_ports   
import serial
import threading
import requests 
import re
import webbrowser
app = Flask(__name__)
CORS(app)
# path= (os.path.join(sys._MEIPASS, 'config\config.json'))
path= (os.path.join(sys._MEIPASS, 'config/config.json'))
# path = "config/config.json"
config = json.loads(open(path).read())
url= config['url']


def lectura():
    while True :
            print ("ciclo")
            ports = serial.tools.list_ports.comports()
            for p in ports :
                if(p.manufacturer):
                    if(p.manufacturer.find("Prolific")!=-1):
                        final = p.device
            if final !="":
                while True :            
                    value = 0
                    print("ciclo lectura inicial")
                    # try:
                    ser = serial.Serial(final, 9600 , timeout=5)
                    data = ser.read_until("kg")
                    ser.close()
                    if len(data) > 1  :
                        print("leyendo")
                        dataSend = {'line':config['line'],
                                    "ok":"MessageL",
                                    'num': "Leyendo datos"}
                        r = requests.post(url = url+"/info", data = dataSend) 
                        count = 1
                        m = re.search("\d+\.\d+",data[0:len(data)-2])
                        num = m.group()
                        value = float(num)
                        while len(data) > 1 :
                            ser = serial.Serial(final, 9600,timeout=config['timeout'])
                            data = ser.read_until("kg")
                            if len(data) > 1:
                                print("leyendo")
                            else :
                                dataSend = {'line':config['line'],
                                            "ok":"Num",
                                            'num': str(value)+" kg"}
                                r = requests.post(url = url+"/updateData", data = dataSend) 
                                data = ""
                            ser.close()
                    else :
                        print("esperando datos")
                        dataSend = {'line':config['line'],
                                     "ok":"MessageL",
                                     'num': "Esperando datos"}
                        r = requests.post(url = url+"/info", data = dataSend)
                        time.sleep(1)
            else :
                print("error conexion con sensor")
                dataSend = {'line':config['line'],
                            'ok':'MessageL',
                            'num': 'Error de conexion con sensor'}
                r = requests.post(url = url+"/info", data = dataSend)
                time.sleep(2)
            time.sleep(2)


threading.Thread(target = lectura).start()



@app.route('/getConfig',methods=['GET'])
def getConfig():

    leer = json.loads(open(path).read())
    return jsonify(leer)

@app.route('/setConfig',methods=['POST'])
def setConfig():
    leer = json.loads(open(path).read())
    if (request.json['name'] == "weight"):
        leer['weight']=request.json['value']
    elif (request.json['name'] == "counter"):
        leer['counter']=request.json['value']
    elif (request.json['name'] == "line"):
        leer['line']=request.json['value']
    elif (request.json['name'] == "test"):
        leer['test']=request.json['value']
    with open(path, 'w') as file:
        json.dump(leer, file, indent=4)
    leer = json.loads(open(path).read())
    return jsonify(leer)

# chrome_path = '/usr/bin/google-chrome %s'
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
webbrowser.get(chrome_path).open("0.0.0.0:3000/recepcion-de-linea",new=1)
if __name__ == '__main__':
        app.run(debug =True , port= 8001)