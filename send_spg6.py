#import software
import struct
import time
import serial
import sys
import datetime


ev3PortBase = '/dev/rfcomm'
# a number will be appended to try to open it.  This is supposed to be the bluetooth port
timeStart = datetime.datetime.now()

for n in range(0,100):
    ev3Port = ev3PortBase + str(n)
##        print('Trying port {}'.format(ev3Port))
    try:
        EV3 = serial.Serial(ev3Port)
    except serial.SerialException:
        continue
    else:
        print('Opened EV3 Brick on {}'.format(ev3Port))
        break
else:       # If no port are found
    print('EV3 does not appear to be open on any /dev/rfcomm port')
    sys.exit()

#create function with inputs for mailbox, message, message type (number, text, logic)
def messageGuin(boxName,message,messageType):
        mType=False
        #change message length based on type on message
        if messageType == "text":
                length = len(boxName) + len(message) + 10
                mType = True
        if messageType == "logic":
                length = len(boxName) + 12
                mType = True
        if messageType == "number":
                length = len(boxName) + 16
                mType = True
        if mType:
                # add chars to message
                btMessage = [ chr(0) for temp in range (0,length)]
                btMessage[2] = chr(1)
                btMessage[4] = chr(0x81)
                btMessage[5] = chr(0x9E)
                btMessage[6] = chr(len(boxName) + 1)
                btMessage[7:7+len(boxName)] = boxName
                payloadPointer = 8 + len(boxName)
                #add different chars based on message type
                if messageType == "text" :
                        btMessage[payloadPointer] = chr((len(message) + 1) & 0xff)
                        btMessage[payloadPointer + 1] = chr((len(message) + 1) >> 8)
                        btMessage[payloadPointer + 2:len(message)] = message
                        endPoint = payloadPointer + len(message) + 1
                if messageType == "logic" :
                        btMessage[payloadPointer] = chr(2)
                        btMessage[payloadPointer + 1] = chr(0)
                        if message == True:
                                btMessage[payloadPointer + 2] = chr(1)
                        endPoint = payloadPointer + 2
                if messageType == "number":
                        btMessage[payloadPointer] = chr(4)
                        btMessage[payloadPointer + 2:] = struct.pack('f',message)
                        endPoint = payloadPointer + 4
                btMessage[0] = chr((endPoint & 0xff))
                btMessage[1] = chr(endPoint >> 8)
                return btMessage #output the converted message
        else: #output error message
                print "Bad Message"
                return "error"

def messageSend(message): #make send message function
        if EV3.isOpen() == True: #check if ev3 is connected
                for n in range(0, 2 + ord(message[0]) + (ord(message[1]) * 256 )): #run different amount of times based on the message
                        EV3.write(message[n]) #send message

for t in range(0,100):  #send message 100 times
        m = messageGuin("EV3Text","hi " + str(t),"text")  #  convert message
        print('Sending msg {}'.format(t))
        messageSend(m) # send converted message
        time.sleep(1.0) # wait between messages
        
EV3.close() # close EV3 connection
