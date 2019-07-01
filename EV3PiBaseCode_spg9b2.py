#! /usr/bin/env python
# import packages
import serial
import time
import datetime
import struct
import os

def printSerIntInfo(ser):
    #print('End Device Name {}  Port = {}  Baud Rate = {}   IsOpen = {}\n  XonXoff = {}'.format(ser.name,
    #    ser.port, ser.baudrate, ser.isOpen(), ser.xonxoff))
    print(ser.get_settings())
 
##    print('Settings: {}'.format(ser.getSettingsDict()))
##    print('Num bytes in waiting = {}   isOpen = {}'.format(ser.inWaiting(), ser.isOpen()))
##    print('CD {}   CTS {}   DSR {}   RI {}'.format(ser.getCD(), ser.getCTS(), ser.getDSR(), ser.getRI()))


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
##    EV3 = serial.Serial('/dev/rfcomm5',timeout=1)   
##    printSerIntInfo(EV3)
    
    global EV3

    timeStart = datetime.datetime.now()
    ev3PortOpen = openEv3()               #Port ID if successful, False otherwise

    if ev3PortOpen:
        print('Opened EV3 Brick on {}'.format(ev3PortOpen))
    else:       # If no port are found
        
        print('EV3 does not appear to be open on any /dev/rfcomm port')
        sys.exit()
 

    #Debugging
##    print('End device name = ',EV3.name)
##    print('Baud rate = ', EV3.baudrate)

    timeLastRx = datetime.datetime.now()
    print("Local Time Now ",format(timeLastRx))

    RxToPeriod = 5      #Seconds.  This is the amount of time that can pass before doing a buffer reset


    while 1:
##            print('Time {}   CD {}   CTS {}   DSR {}   RI {}   InWaiting {}'.format(datetime.datetime.now().time(), EV3.getCD(),
##                EV3.getCTS(), EV3.getDSR(), EV3.getRI(), EV3.inWaiting()))


            if EV3.inWaiting() >= 2: # check for ev3 message
##                print('inWaiting = {}'.format(EV3.inWaiting()))
                # Get the number of bytes in this message
                s = EV3.read(2)
                # struct.unpack returns a tuple unpack using []
                
                [numberOfBytes] = struct.unpack("<H", s)
##                print numberOfBytes,
                # Wait for the message to complete
##                print("{}   Expecting num of bytes {}".format(datetime.datetime.now().time(), numberOfBytes))
                while EV3.inWaiting() < numberOfBytes:
                    print "Waiting at point 1"
                    print "Expecting num of bytes", numberOfBytes
                    time.sleep(0.01)
                #read number of bytes
                s = s + EV3.read(numberOfBytes)
##                print('s = {}'.format(s))
                s = s[6:]
                # Get the mailboxName
                mailboxNameLength = ord(s[0])
                mailboxName = s[1:1+mailboxNameLength-1]
##                print mailboxName,
                s = s[mailboxNameLength+1: ]
                # Get the message text
                [messageLength] = struct.unpack("<H", s[0:2])
                message = s[2:2+messageLength]
                timeLastRx = datetime.datetime.now()
                print('{}; Num of Bytes = {}   Timenow {}; TimeLastRx  {};  inWaiting = {}'.format(message, numberOfBytes,
                    datetime.datetime.now().time(), timeLastRx.time(), EV3.inWaiting()))
 
                #print message

##                timeLastRx = datetime.datetime.now()
##                if 'hi' in message:
##                    print "Hello EV3"
            elif EV3.inWaiting() == 1:
                print('inWaiting = 1;  timenow is {}'.format(datetime.datetime.now().time()))
##                printSerIntInfo(EV3)
                time.sleep(0.01)
            else:
                # See if a buffer reset is needede
                timeNow = datetime.datetime.now()
                timeSinceLastRx = timeNow - timeLastRx
                #secSinceLastRx = timeSinceLastRx.second + timeSinceLastRx.microsecond/1000000
                secSinceLastRx = timeSinceLastRx.total_seconds()
                # print "Time Since Last Rx: ", timeSinceLastRx
                if secSinceLastRx > RxToPeriod:
                    # EV3.flushInput
                    #EV3.close()
                    #EV3.open()
                    timeLastRx = timeNow                   # Prevents repetitive flushing
                    m = messageGuin("BT","Fr RPi BT CLEAR","text")  #  convert message; message instructs EV3 to clear BT interface
                    print('** Sending EV3 BT CLEAR ')
                    messageSend(EV3, m) # send converted message
                    EV3.flush()
                    time.sleep(7.0)            # wait 5 sec between messages.  This was found
                                        #experimentally to be the approx the lowest delay that
                                        #the EV3 and RPi can deal with
                    ev3PortOpen = openEv3()               #Tryt to reopen port because the BT message just caused the

                    #print("*** Flushed at ",timeNow)
##                    print("Waiting at point 2 at {}".format(datetime.datetime.now().time()))
                    #in_wait = EV3.inWaiting()
                    #print "Num of bytes waiting = ", in_wait
##                    printSerIntInfo(EV3)
##                    EV3.flush()
##                    EV3.reset_input_buffer()
##                    EV3.reset_output_buffer()
                # No data is ready to be processed yield control to system
                time.sleep(0.01)

if __name__ == "__main__":
    main()