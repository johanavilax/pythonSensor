# -*- coding: utf-8 -*-
import serial.tools.list_ports   # import serial module
import serial

final = ""
ports = serial.tools.list_ports.comports()
for p in ports :
    if(p.manufacturer):
        if(p.manufacturer.find("Prolific")!=-1):
            final = p.device
if (final != ""):
    while True:
            ser = serial.Serial(final, 9600)
            data = ser.read_until("kg")
            if len(data) > 0:
                  print("esto es data "+ data)
            ser.close()
else :
    print("Sensor no encontrado")