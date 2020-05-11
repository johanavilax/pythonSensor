import eventlet
eventlet.monkey_patch()


from flask import Flask ,jsonify ,request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import serial.tools.list_ports   
import serial
import json
import time
from time import time as tiempo
import re


import statistics as stats

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app,logger=True,cors_allowed_origins='*',always_connect = True,engineio_logger=True,ping_timeout=9999 ,ping_interval=9999)

final = ""
connected = False
connectedC = False
config = json.loads(open('config.json').read())

@app.route('/getConfig',methods=['GET'])
def getConfig():
    leer = json.loads(open('config.json').read())
    return jsonify(leer)

@app.route('/setConfig',methods=['POST'])
def setConfig():
    leer = json.loads(open('config.json').read())
    if (request.json['name'] == "weight"):
        leer['weight']=request.json['value']
    elif (request.json['name'] == "counter"):
        leer['counter']=request.json['value']
    elif (request.json['name'] == "line"):
        leer['line']=request.json['value']
    elif (request.json['name'] == "test"):
        leer['test']=request.json['value']
    with open('config.json', 'w') as file:
        json.dump(leer, file, indent=4)
    leer = json.loads(open('config.json').read())
    return jsonify(leer)


@socketio.on('connect',namespace='/calibrate')
def connectC():
    global connectedC
    connectedC = True
    print("calibrate")

    while connectedC: 
        ports = serial.tools.list_ports.comports()
        for p in ports :
            if(p.manufacturer):
                if(p.manufacturer.find("Prolific")!=-1):
                    final = p.device
        if final !="":
            socketio.emit('infoC', {"ok":"MessageL",'num': "Porfavor bloquee el sensor"}, namespace='/calibrate')
            try:
                ser = serial.Serial(final, 9600)
                data = ser.read_until("kg")
                ser.close()
                if len(data) > 1  :
                    socketio.emit('infoC', {"ok":"MessageC",'num': "Leyendo datos Porfavor espere"}, namespace='/calibrate')
                    lista = []
                    for i in range(10):
                        start_time = tiempo()
                        ser = serial.Serial(final, 9600)
                        data = ser.read_until("kg")
                        elapsed_time = tiempo() - start_time
                        lista.append(elapsed_time)
                        ser.close()
                    media = stats.mean(lista)
                    config['timeout'] = (media+(media*5/100))
                    with open('config.json', 'w') as file:
                            json.dump(config, file, indent=4)
                    socketio.emit('infoC', {"ok":"C",'num': "Terminado"}, namespace='/calibrate')
                    connectedC = False
            except serial.SerialException:
                final == ""
                socketio.emit('infoC', {"ok":"E",'num': "Problema con el puerto, reconectando"}, namespace='/calibrate')
                while final == "":
                    ports = serial.tools.list_ports.comports()
                    for p in ports :
                        if(p.manufacturer):
                            if(p.manufacturer.find("Prolific")!=-1):
                                final = p.device
            

@socketio.on('disconnect',namespace='/calibrate')
def disconnectC():
    global connectedC
    connectedC = False

@socketio.on('connect',namespace='/socket')
def connect():
    print("connected")
    global connected
    global final
    connected = True
    while connected == True :
        print ("ciclo")

        ports = serial.tools.list_ports.comports()
        for p in ports :
            if(p.manufacturer):
                if(p.manufacturer.find("Prolific")!=-1):
                    final = p.device
        if final !="":
            while connected == True :            
                value = 0
                count = 0
                print("ciclo lectura inicial")
                # try:
                ser = serial.Serial(final, 9600 , timeout=5)
                data = ser.read_until("kg")
                ser.close()
                if len(data) > 1  :
                    print("leyendo")
                    socketio.emit('info', {"ok":"MessageL",'num': "Leyendo datos"}, namespace='/socket')
                    count = 1
                    m = re.search("\d+\.\d+",data[0:len(data)-2])
                    num = m.group()
                    value = float(num)
                    while len(data) > 1 :
                        ser = serial.Serial(final, 9600,timeout=config['timeout'])
                        data = ser.read_until("kg")
                        if len(data) > 1:
                            m = re.search("\d+\.\d+",data[0:len(data)-2])
                            num = m.group()
                            value = float(num) + value
                            count = count + 1
                        else :
                            socketio.emit('sensorData', {"ok":"Num",'num': str(value/count)+" kg"}, namespace='/socket')
                            data = ""
                        ser.close()
                else :
                    print("esperando datos")
                    socketio.emit('info', {"ok":"MessageL",'num': "Esperando datos"} , namespace='/socket')
                    socketio.sleep(2)

                # except serial.SerialException:
                #     print(serial.SerialException)
                #     final = ""
                #     print("Error leyenndo datos")
                #     socketio.emit('info', {"ok":"MessageE",'num': "Error con puerto , reconectando"} , namespace='/socket')
                #     socketio.sleep(2)
        else :
            print("error conexion con sensor")
            socketio.emit('info', {"ok":"MessageL",'num': "Error de conexion con sensor"} , namespace='/socket')
            socketio.sleep(2)
        socketio.sleep(2)

@socketio.on('disconnect',namespace='/socket')
def disconnect(environ):
    print("discconect")
    print(environ)
    global connected
    connected = False
    
@socketio.on('ping',namespace='/socket')
def ping():
    print("ping")
@socketio.on('pong',namespace='/socket')
def pong():
    print("pong")
 
if __name__ == '__main__':
    
    socketio.run(app,debug =True , port= 8001)


