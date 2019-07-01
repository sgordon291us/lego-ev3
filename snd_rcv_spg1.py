#! /usr/bin/env python
# import packages
import serial
import time
import datetime
##import deltatime
import struct
import os
import sys


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

def messageSend(dest_ev3, message): #make send message function
        if dest_ev3.isOpen() == True: #check if ev3 is connected
                for n in range(0, 2 + ord(message[0]) + (ord(message[1]) * 256 )): #run different amount of times based on the message
                        dest_ev3.write(message[n]) #send message


def main():
      
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


    # Only if port is opened
    print('Time is {}; inWaiting() is {}'.format(datetime.datetime.now().time(), EV3.inWaiting()))    

    while 1:
        
            timeFromStart = datetime.datetime.now() - timeStart
##                print('Time {}   inWaiting  {} cts {}   dsr {}   dsrdtr {}   fd {}   CD {}   CTS {}   DSR {}   RI {}'.format(timeFromStart,EV3.inWaiting(),
##                    EV3.cts, EV3.dsr, EV3.dsrdtr, EV3.fd, EV3.getCD(), EV3.getCTS(), EV3.getDSR(), EV3.getRI()))

            
            try:
                if EV3.inWaiting() >= 2: # check for ev3 message
                    # Get the number of bytes in this message
                    s = EV3.read(2)
                    # struct.unpack returns a tuple unpack using []
                    [numberOfBytes] = struct.unpack("<H", s)
##                    print numberOfBytes,
                    # Wait for the message to complete
                    while EV3.inWaiting() < numberOfBytes:
                        time.sleep(0.01)
                    #read number of bytes
                    s = s + EV3.read(numberOfBytes)
                    s = s[6:]
                    # Get the mailboxName
                    mailboxNameLength = ord(s[0])
                    mailboxName = s[1:1+mailboxNameLength-1]
##                    print mailboxName,
                    s = s[mailboxNameLength+1: ]
                    # Get the message text
                    [messageLength] = struct.unpack("<H", s[0:2])
                    message = s[2:2+messageLength]
                    timeFromStart = datetime.datetime.now() - timeStart
                    print('Time: {}   Msg: {}   Num bytes = {}'.format(timeFromStart, message,numberOfBytes))
                    
                else:
                    # No data is ready to be processed yield control to system
                    time.sleep(0.01)            
            
            except KeyboardInterrupt:
                sys.exit(0)
            


if __name__ == "__main__":
    main()

