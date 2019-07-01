#! /usr/bin/env python
#import software
import struct
import time
import serial
import sys
import datetime
import os



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
                        
def openEv3():
#This procedure runs through the /dev/rfcommx ports starting at 0 and going up to 100.  It will open
#try each rfcommx port and open the first one that is successful.  It will return port that is successful
#or False if none are successful
    global EV3
    
    ev3PortBase = '/dev/rfcomm'
    # a number will be appended to try to open it.  This is supposed to be the bluetooth port

    for n in range(0,100):
        ev3Port = ev3PortBase + str(n)
    ##        print('Trying port {}'.format(ev3Port))
        try:
            EV3 = serial.Serial(ev3Port)
        except serial.SerialException:
            continue
        else:
            #print('Opened EV3 Brick on {}'.format(ev3Port))
            return ev3Port
            break
    else:       # If no port are found
        #print('EV3 does not appear to be open on any /dev/rfcomm port')
        return False
        #sys.exit()

def main():
    
    global EV3

    timeStart = datetime.datetime.now()
    ev3PortOpen = openEv3()               #Port ID if successful, False otherwise

    if ev3PortOpen:
        print('Opened EV3 Brick on {}'.format(ev3PortOpen))
    else:       # If no port are found
        
        print('EV3 does not appear to be open on any /dev/rfcomm port')
        sys.exit()

    try:
        for t in range(0,100):  #send message 100 times
                m = messageGuin("BT","Fr RPi " + str(t),"text")  #  convert message
                print('Sending msg {}'.format(t))
                messageSend(EV3, m) # send converted message
                time.sleep(5.0) # wait between messages
                ev3PortOpen = openEv3()               #Tryt to reopen port because the BT message just caused the
                                                    #EV3 to close and open it
                if not ev3PortOpen:
                    print('** BT port to EV3 could not be re-opened')
                    break
                else:
                    print('Port opened after message {}'.format("BT  "+"Fr RPi " + str(t)))
                    
                
    except KeyboardInterrupt:
       pass
            
    EV3.close() # close EV3 connection
    sys.exit()
    
if __name__ == "__main__":
    main()
