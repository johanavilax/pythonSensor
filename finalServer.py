import eventlet
eventlet.monkey_patch()


import time
from flask import Flask ,jsonify ,request
from flask_socketio import SocketIO, emit
import json
import os
import sys
from flask_cors import CORS
import serial.tools.list_ports   
import serial
import threading
import requests 
import re
# import webbrowser
app = Flask(__name__) 
CORS(app)
# path= (os.path.join(sys._MEIPASS, 'config\config.json'))
# path= (os.path.join(sys._MEIPASS, 'config/config.json'))
path = "config/config.json"
config = json.loads(open(path).read())
url= config['url']
socketio = SocketIO(app,logger=True,cors_allowed_origins='*',always_connect = True,engineio_logger=True,ping_timeout=9999 ,ping_interval=9999)

try:
    if llamado == False :
        llamado = True
except:
    llamado = False
start = False

def enviar(dest,data):
    global url
    try :
        # r = requests.post(url = url+":4000/"+dest, data = data) 
        socketio.emit(dest,data, namespace='/socket')

    except :
        print("error enviando al servidor")


def lectura():
    global start
    while start :
            ports = serial.tools.list_ports.comports()
            final = ""
            for p in ports :
                if(p.manufacturer):
                    if(p.manufacturer.find("Prolific")!=-1):
                        final = p.device
            if final !="":
                while start :            
                    value = []
                    data = ""
                    dataSend = {'line':config['line'],
                                    "ok":"MessageL",
                                    'num': "Esperando datos"}
                    try:
                        threading.Thread(target = enviar, args=("info",dataSend) ).start() 
                    except:
                        print("Error enviando informacion")
                    try:
                        ser = serial.Serial(final, 9600 , timeout=1)
                        data = ser.read_until(str.encode("kg"))
                        ser.close()
                    except ValueError:
                        print("algo ocurrio con sensor"+ str(ValueError))
                    if len(data) > 1:
                        dataSend = {'line':config['line'],
                                    "ok":"MessageL",
                                    'num': "Leyendo datos"}
                        try:
                            threading.Thread(target = enviar, args=("info",dataSend) ).start() 
                        except:
                            print("problema al conectar con el servidor")
                        try:
                            value.append(data.decode("utf-8") )
                        except:
                            print("error convirtiendo a float")
                        while len(data) > 1 :
                            try:
                                ser = serial.Serial(final, 9600,timeout=config['timeout'])
                                data = ser.read_until(str.encode("kg"))
                                ser.close()
                            except:
                                print("error con sensor en lectura")
                            if len(data) > 1:
                                value.append(data.decode("utf-8") )
                                print(data)
                            else :
                                data = " "
                                dataSend = {'line':config['line'],
                                            "ok":"Num",
                                            'num': value}
                                
                                try: 
                                    print(value)
                                    threading.Thread(target = enviar, args=("updateData",dataSend) ).start() 
                                    print("enviada")
                                except : 
                                    print ("error enviando datos ")
                                print("despues")
                        print("salio")
                    else :
                        dataSend = {'line':config['line'],
                                     "ok":"MessageL",
                                     'num': "Esperando datos"}
                        try:
                            threading.Thread(target = enviar, args=("info",dataSend) ).start() 
                        except:
                            print("Error enviando informacion")
                        time.sleep(0.5)
            else :
                print("error conexion con sensor")
                dataSend = {'line':config['line'],
                            'ok':'MessageL',
                            'num': 'Error de conexion con sensor'}
                try:
                    threading.Thread(target = enviar, args=("info",dataSend) ).start() 
                except:
                    print("Error enviando informacion de sensor")
                time.sleep(2)
            time.sleep(2)


@app.route('/start',methods=['GET'])
def start():
    global start
    if not start :
        start = True
        threading.Thread(target = lectura).start()
        return jsonify({"ok":"ok"})

@app.route('/end',methods=['GET'])
def stop():
    global start
    start = False
    return jsonify({"ok":"ok"})

@app.route('/getConfig',methods=['GET'])
def getConfig():
    print("get")
    leer = json.loads(open(path).read())
    return jsonify(leer)

@app.route('/setConfig',methods=['POST'])
def setConfig():
    global config
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
    config = json.loads(open(path).read())
    return jsonify(leer)

# @app.before_first_request
# def loop():
#     threading.Thread(target = lectura).start()


# def open_browser():
#      global llamado
#      print(llamado)
#      if not llamado:
#          llamado = True
#          print(llamado)
#          chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
#          time.sleep(5)
#         #  chrome_path = '/usr/bin/google-chrome %s'
#          webbrowser.get(chrome_path).open(url+"/recepcion-de-linea")  

if __name__ == '__main__':
        # threading.Thread(target = open_browser).start()
        # app.run(debug =True  ,port= 8001,use_reloader=False)    
        socketio.run(app,debug =True , port= 8001)