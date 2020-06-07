#!/usr/bin/python2.7
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
#path= (os.path.join(sys._MEIPASS, 'config\config.json'))
# path= (os.path.join(sys._MEIPASS, 'config/config.json'))
path = "config/config.json"
config = json.loads(open(path).read())
url= config['url']
try:
    if llamado == False :
        llamado = True
except:
    llamado = False


def enviar(dest,data):
    global url
    try :
        r = requests.post(url = url+":4000/"+dest, data = data) 
    except :
        print("error enviando al servidor")


def lectura():
    while True :
            print ("ciclo")
            ports = serial.tools.list_ports.comports()
            final = ""
            for p in ports :
                if(p.manufacturer):
                    if(p.manufacturer.find("Prolific")!=-1):
                        final = p.device
            if final !="":
                while True :            
                    value = []
                    print("ciclo lectura inicial")
                    data = ""
                    dataSend = {'line':config['line'],
                                    "ok":"MessageL",
                                    'num': "Esperando datos"}
                    try:
                        threading.Thread(target = enviar, args=("info",dataSend) ).start() 
                    except:
                        print("Error enviando informacion")
                    try:
                        ser = serial.Serial(final, 9600 , timeout=0.6)
                        data = ser.read_until("kg")
                        ser.close()
                    except Exception,e :
                        print("algo ocurrio con sensor",str(e))
                        pass
                    if len(data) > 1  :
                        print("leyendo")
                        dataSend = {'line':config['line'],
                                    "ok":"MessageL",
                                    'num': "Leyendo datos"}
                        try:
                            threading.Thread(target = enviar, args=("info",dataSend) ).start() 
                        except:
                            print("problema al conectar con el servidor")
                        try:
                            value.append(data+ " kg")
                        except Exception , e:
                            print("error convirtiendo a float",str(e))
                        while len(data) > 1 :
                            try:
                                ser = serial.Serial(final, 9600,timeout=config['timeout'])
                                data = ser.read_until("kg")
                                value.append(data+" kg")
                                ser.close()
                            except:
                                print("error con sensor en lectura")
                            if len(data) > 1:
                                print("leyendo caja")
                            else :
                                data = " "
                                dataSend = {'line':config['line'],
                                            "ok":"Num",
                                            'num': (value)}
                                print(value)
                                print(len(value))
                                print(dataSend)
                                try: 
                                    
                                    threading.Thread(target = enviar, args=("updateData",dataSend) ).start() 
                                    print("enviada")
                                except AssertionError as error:
                                    print(error)
                                    print ("error enviando datos ")
                                print("despues")
                        print("salio")
                    else :
                        print("esperando datos")
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

@app.before_first_request
def loop():
    threading.Thread(target = lectura).start()


def open_browser():
     global llamado
     print(llamado)
     if not llamado:
         llamado = True
         print(llamado)
         chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
         time.sleep(5)
        #  chrome_path = '/usr/bin/google-chrome %s'
         webbrowser.get(chrome_path).open(url+"/recepcion-de-linea")  

if __name__ == '__main__':
        threading.Thread(target = open_browser).start()
        app.run(debug =True  ,port= 8001,use_reloader=False)