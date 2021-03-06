#!/usr/bin/python3
from os import environ
from serial import Serial 
import Adafruit_BBIO.GPIO as GPIO
import sys

CODE = sys.argv[1]
print(CODE)

GPIO.setup("P8_11", GPIO.IN)
GPIO.setup("P8_12", GPIO.IN)

print(GPIO.input("P8_11"))
print(GPIO.input("P8_12"))


if GPIO.input("P8_11") == 1 and GPIO.input("P8_12") == 1:
    print('PRU_FONTES' + CODE)
    exit()

port = '/dev/ttyUSB0'
''' 
    Iterar pelos possíveis baudrates testando todas as possibilidades
    de comandos. Isso deverá ser repetido até alguém responder.

    Com isso saberemos o baudrate da aplicação e com quem estamos lidando.
    
    Por enquanto isso irá funcionar apenas para FTDI, não dando suporte a aplaicações 
    que fazem uso da interface PRU.
    
    
'''

cmds = [
    {
        'baud' : 115200,
        'msg' : ['TORRE1','TORRE2'],
        'device':'rf-booster-tower'
    },
    {
        'baud' : 115200,
        'msg' :  ['RACK1','RACK2','RACK3','RACK4'],
        'device':'rf-ring-tower'
    },
    {
        'baud':115200,
        'msg':[0x10, 0x00, 0x01, 0x1], #?
        'device':'mbtemp'
    },
    {
        'baud':9600,
        'msg': '?',
        'device': 'agilent4uhv'
    }
]

die = False
while True:
    for cmd in cmds:
        ser = None
        try:
            res = None
            ser = Serial(port, cmd.get('baud'), timout=0.5)

            if cmd.get('device') == 'mbtemp':
                for i in range(1,32):
                    pass
            elif cmd.get('device') == 'agilent4uhv':
                pass
                
        except:
            pass
        finally:
            if ser:
                ser.close()
        if die:
            exit()
    pass
