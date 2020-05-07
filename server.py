import eventlet
eventlet.monkey_patch()


from flask import Flask ,jsonify ,request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import serial.tools.list_ports   
import serial
import json
import time
import threading






app = Flask(__name__)
CORS(app)
socketio = SocketIO(app,cors_allowed_origins='*',always_connect = True)

final = ""
connected = False

def sensorCiclo():
    global final
    global connected
    while True :
        while final == "" and connected == True:
            print ("ciclo")

            ports = serial.tools.list_ports.comports()
            for p in ports :
                if(p.manufacturer):
                    if(p.manufacturer.find("Prolific")!=-1):
                        final = p.device
            if final !="":
                while connected == True:
                    ser = serial.Serial(final, 9600)
                    data = ser.read_until("kg")
                    if len(data) > 0:
                        print("esto es data "+ str(data))
                        socketio.emit('sensorData', {'num': str(data)}, namespace='/socket')
                    else :
                        emit('sensorData', {'num': "Error de conexion con sensor"})
                    ser.close()
            else :
                emit('sensorData', {'num': "Error de conexion con sensor"})
        time.sleep(2)

threading.Thread(target=sensorCiclo).start()

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

@socketio.on('connect',namespace='/socket')
def connect():
    print("connected")
    global connected
    connected = True
    # while final == "" and connected == True:
    #     print ("ciclo")

    #     ports = serial.tools.list_ports.comports()
    #     for p in ports :
    #         if(p.manufacturer):
    #             if(p.manufacturer.find("Prolific")!=-1):
    #                 final = p.device
    #     if final !="":
    #         while final!="":
    #             ser = serial.Serial(final, 9600)
    #             data = ser.read_until("kg")
    #             if len(data) > 0:
    #                 print("esto es data "+ str(data))
    #                 socketio.emit('sensorData', {'num': str(data)}, namespace='/socket')
    #             else :
    #                 emit('sensorData', {'num': "Error de conexion con sensor"})
    #             ser.close()
    #     else :
    #         emit('sensorData', {'num': "Error de conexion con sensor"})
@socketio.on('disconnect',namespace='/socket')
def disconnect():
    print("discconect")
    global final
    global connected
    final = ""
    connected = False

if __name__ == '__main__':
    
    socketio.run(app,debug =True , port= 8001)


