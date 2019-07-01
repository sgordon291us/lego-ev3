#! /usr/bin/env python
#This code allows simple control of the EV3 from the RPi using a text interface.
#Based on a text command from teh user, this will send a message to the EV3 to
#perform an action.  Valid actions are:
#FORWARD, REVERSE, STOP.
#Other commands are
#EXIT, END
#The it sould not be case-sensitiive to the input taken from the user, but the message
#send to the EV3 IS case-sensitive 
import serial
import time
import datetime
import struct
import os
import sys

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
                        
def messageRcv(srcEv3, maxWait=4):
#This procedure receies a message from the EV3.  The inputs are the EV3 interface on src_ev3 and the maximum wait
#time maxWait in seconds.  After the maxWait time, it will return with None.  The value returned is the text of the
#message from the EV3
    
    global RxToPeriod
    
    timeStart = datetime.datetime.now()
    timeLastRx = timeStart                       # Initialize this so you dont get an error on first compare
    while (datetime.datetime.now() - timeStart).total_seconds() < maxWait:
##            print('Time {}   CD {}   CTS {}   DSR {}   RI {}   InWaiting {}'.format(datetime.datetime.now().time(), EV3.getCD(),
##                EV3.getCTS(), EV3.getDSR(), EV3.getRI(), EV3.inWaiting()))


        if srcEv3.inWaiting() >= 2: # check for ev3 message
##                print('inWaiting = {}'.format(EV3.inWaiting()))
            # Get the number of bytes in this message
            s = srcEv3.read(2)
            # struct.unpack returns a tuple unpack using []
            
            [numberOfBytes] = struct.unpack("<H", s)
##                print numberOfBytes,
            # Wait for the message to complete
##                print("{}   Expecting num of bytes {}".format(datetime.datetime.now().time(), numberOfBytes))
            while srcEv3.inWaiting() < numberOfBytes:
                print "Waiting at point 1"
                print "Expecting num of bytes", numberOfBytes
                time.sleep(0.01)
            #read number of bytes
            s = s + srcEv3.read(numberOfBytes)
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
#                print message
##                timeLastRx = datetime.datetime.now()
##                if 'hi' in message:
##                    print "Hello EV3"
        elif srcEv3.inWaiting() == 1:
            # The message is only partially received, so wait a little longer
##            print('inWaiting = 1;  timenow is {}'.format(datetime.datetime.now().time()))
##                printSerIntInfo(EV3)
            time.sleep(0.01)
        else:
            # Nothing was received, so either wait for another period or perform
            # a buffer clear or reset, if desired
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
##                reset_bt_if()
            # No data is ready to be processed yield control to system
            time.sleep(0.01)
    else:
        return None
                
def reset_bt_if():
    #Bluetooth interface reset
    
    global EV3
    
    m = messageGuin("BT","Fr RPi BT CLEAR","text")  #  convert message; message instructs EV3 to clear BT interface
    print('** Sending EV3 BT CLEAR ')
    messageSend(EV3, m) # send converted message
    time.sleep(7.0)            # wait 5 sec between messages.  This was found
                        #experimentally to be the approx the lowest delay that
                        #the EV3 and RPi can deal with
    ev3PortOpen = openEv3()               #Tryt to reopen port because the BT message just caused the

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
    
    global secSinceLastRx, RxToPeriod
    
##    global EV3

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
    maxRxWait = 4       #Max time in sec to wait for message from EV3
    
    try:
    
        while True:
    ##        userCmd = input('Command? ')                     # REALLY NOT SURE WHAT THE PROBLEM HERE IS
            userCmd = "RVS"                                   #shoulf be taken out
            print('** COMMAND IS {}'.format(userCmd))
            userCmdUpper = userCmd.upper()
    ##        userCmd = input('Command? ')
            print('** COMMAND IS {}'.format(userCmdUpper))
            
            if "FORWARD" == userCmdUpper or "FWD" == userCmdUpper:
                ev3Msg = "FWD"
            elif "BACK" == userCmdUpper or "BACKWARDS" == userCmdUpper or "RVS" == userCmdUpper or "REVERSE" == userCmdUpper:
                ev3Msg = "RVS"
            elif "STOP" == userCmdUpper:
                ev3Msg = "STOP"
            elif "EXIT" == usrCmdUpper or "END" == userCmdUpper:
                break
            else:
                ev3Msg = None
                
            if ev3Msg is not None:
                m = messageGuin("EV3-CMD",ev3Msg,"text")  #  convert message; select EV3-CMD block to send to
                print('Sending to EV3 msg {}'.format(ev3Msg))
                messageSend(EV3, m) # send converted message
            else:
                print('** Error with {}'.format(userCmd))
                
            time.sleep(5)                                # Just slow the loop a little
                
    except KeyboardInterrupt:
        # Send a stop message and stop the robot
        ev3Msg = "STOP"
        m = messageGuin("EV3-CMD",ev3Msg,"text")  #  convert message; select EV3-CMD block to send to
        print('Sending to EV3 msg {}'.format(ev3Msg))
        messageSend(EV3, m) # send converted message

    
    EV3.close()
    sys.exit()
            
##
##    # Do this loop untilk user stops it.
##    t = 0
##    try:
##        while True:
##    ##            print('Time {}   CD {}   CTS {}   DSR {}   RI {}   InWaiting {}'.format(datetime.datetime.now().time(), EV3.getCD(),
##    ##                EV3.getCTS(), EV3.getDSR(), EV3.getRI(), EV3.inWaiting()))
##
##            message = messageRcv(EV3, maxRxWait)
##            
##            if message is not None:
##                timeLastRx = datetime.datetime.now()
##                numberOfBytes = len(message)
##                print('{}; Num of Bytes = {}   Timenow {}; TimeLastRx  {};  inWaiting = {}'.format(message, numberOfBytes,
##                    datetime.datetime.now().time(), timeLastRx.time()))
##     
##            
##            m = messageGuin("EV3","Pick up the phone " + str(t),"text")  #  convert message
##            print('Sending msg {}'.format(t))
##            messageSend(EV3, m) # send converted message
##            time.sleep(5.0)            # wait 5 sec between messages.  This was found
##                                    #experimentally to be the approx the lowest delay that
##                                    #the EV3 and RPi can deal with
##            t += 1
##            
##    except KeyboardInterrupt:
##        EV3.close()
##        sys.exit()
        
        

if __name__ == "__main__":
    main() 