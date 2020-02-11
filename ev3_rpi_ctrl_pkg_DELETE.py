#! /usr/bin/env python2
#This code allows simple control of the EV3 from the RPi using a text interface.
#Based on a text command from teh user, this will send a message to the EV3 to
#perform an action.  Valid actions are:
#FORWARD, REVERSE, STOP, JOSHISCOOL
#Other commands are
#EXIT, END
#The it sould not be case-sensitiive to the input taken from the user, but the message
#send to the EV3 IS case-sensitive
# This version (4) has the critical procedures IMPORTED from teh ev3_rpi_ctrl_pkg
import serial
import time
import datetime
import struct
import os
import sys
##import ev3_rpi_ctrl_pkg

def printSerIntInfo(ser):
    #print('End Device Name {}  Port = {}  Baud Rate = {}   IsOpen = {}\n  XonXoff = {}'.format(ser.name,
    #    ser.port, ser.baudrate, ser.isOpen(), ser.xonxoff))
    print(ser.get_settings())
 
##    print('Settings: {}'.format(ser.getSettingsDict()))
##    print('Num bytes in waiting = {}   isOpen = {}'.format(ser.inWaiting(), ser.isOpen()))
##    print('CD {}   CTS {}   DSR {}   RI {}'.format(ser.getCD(), ser.getCTS(), ser.getDSR(), ser.getRI()))


#create function with inputs for mailbox, message, message type (number, text, logic)
def messageGuin(boxName,message,messageType):
    print('*** messageGuin Point 0')
    mType=False
    #change message length based on type on message
    if messageType == "text":
            if len(message) == 0 or message.isspace():
                mtype = False                           #Give and error to a blank message or whitespace
                print('*** Message {} Rejected'.format(message))
            else:
                length = len(boxName) + len(message) + 10
                mType = True
    if messageType == "logic":
            length = len(boxName) + 12
            mType = True
    if messageType == "number":
            length = len(boxName) + 16
            mType = True
    print('*** messageGuin Point 1')
    if mType:
        # add chars to message
        print('*** messageGuin Point 2')
        btMessage = [ chr(0) for temp in range (0,length)]
        btMessage[2] = chr(1)
        btMessage[4] = chr(0x81)
        btMessage[5] = chr(0x9E)
        btMessage[6] = chr(len(boxName) + 1)
        btMessage[7:7+len(boxName)] = boxName
        payloadPointer = 8 + len(boxName)
        #add different chars based on message type
        if messageType == "text" :
                print('*** messageGuin Point 3')
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
        print('*** messageGuin Point 4')
##        print('*** btmessage = {}'.format(btMessage))
##        return None                    # for debugging--DELETE
        return btMessage #output the converted message
    else: #output error message
        print('*** messageGuin Point 5')
        print("Bad Message")
        return "error"
##    print('*** Returning now...')
##    return

# FOR DEBUGGING DELETE THIS PROCEDURE
def messageSendX(d_ev3):
    print("*** EV3 Info:", d_ev3.get_settings())
    return

def messageSendY(xy):
    print("**** EV3 Message {}:",xy)
    return

def messageSend(dest_ev3, message): #make send message function
##    print('**** Point 0, message = ',message)
##    print('**** EV3 type',type(dest_ev3))
##    print('**** EV3 name',dest_ev3.name)
##    print('**** EV3 Settings: name', dest_ev3.name, dest_ev3.get_settings())
    if dest_ev3.isOpen() == True: #check if ev3 is connected
##        print('**** Point 1')
##        print('**** EV3 type',type(dest_ev3))
##        print('**** EV3 name',dest_ev3.name)
##        print('**** EV3 Settings: name', dest_ev3.name, dest_ev3.get_settings())
        for n in range(0, 2 + ord(message[0]) + (ord(message[1]) * 256 )): #run different amount of times based on the message
##            print('**** Point 2; message[{}] = {}'.format(n, message[n]))
            # if __name__ == '__main__':
            dest_ev3.write(message[n]) #send message
##    print('**** Point 3')
    return

def msg_fmt_send(dest_ev3,boxName,ev3Msg,messageType):
    
#This proceudre takes the uinformatted "message" and first performs the needed formatting then
#sends it on the BT in,terface to the EV3.  This procedure was written to try to get around the problem
#with the AIY software in voice_assist_ev3_ctrlx where it generated an error in messageSend.
#Instead
#Params:
#  dest_ev3 is the pointer to the bluetooth serial interface connected the EV3
#  boxName is the label on the EV3 box that is to receive the message (like EV3-CMD"
#  message is the message to send (either a string, number or boolean)
#  type states the type that the mesage is ("text", "logic", "number")
#possible errors are
#   1 No dest EV3 defined
#   2 bluetooth serial interace is not open

    print('** IN msg_fmt_send, message len = {}, isspace() = {}, message is {}'.format(len(ev3Msg), ev3Msg.isspace(), ev3Msg))

    error = 0

    if dest_ev3 is None:
        error = 1                # No dest_ev3 defined
    elif not dest_ev3.isOpen():
        error = 2                # dest_ev3 not open
    elif ev3Msg is not None and len(ev3Msg)>0 and ev3Msg.isspace():         # Discard if no message, length = or is msg is whitespace
        m = messageGuin("EV3-CMD",ev3Msg,"text")  #  convert message; select EV3-CMD block to send to
        print('Sending to EV3 msg: {}'.format(ev3Msg))
        messageSend(dest_ev3, m) # send converted message
    else:
        print('** Error with "{}"'.format(ev3Msg))
        
    return error

    

def messageRcv(srcEv3, maxWait=4):
#This procedure receies a message from the EV3.  The inputs are the EV3 interface on src_ev3 and the maximum wait
#time maxWait in seconds.  After the maxWait time, it will return with None.  The value returned is the text of the
#message from the EV3
    
    RxToPeriod = 5                               # Seconds.  This is the timeout period after which this
                                                # procedure declares the LEGO EV3 not reachable on the BT
                                                # interface.  Right now it takes no action for this situation
    
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
##                print("Waiting at point 1")
##                print("Expecting num of bytes {}".format(numberOfBytes))
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
#try each rfcommx port and open the first one that is successful.  It will return the pointer to the EV3
#     port in text
# and the pointer to the EV#if it is successful.  If not successful, it returns False

##    global EV3
    
    ev3PortBase = '/dev/rfcomm'
    # a number will be appended to try to open it.  This is supposed to be the bluetooth port

    for n in range(0, 100):
        ev3Port = ev3PortBase + str(n)
    ##        print('Trying port {}'.format(ev3Port))
        try:
            local_EV3 = serial.Serial(ev3Port)
        except serial.SerialException:
            continue
        else:
##            print('****** Opened EV3 Brick on {}'.format(ev3Port))
##            print('****** EV3 type', type(local_EV3))
##            print('****** EV3 name', local_EV3.name)
            return local_EV3, ev3Port
            break
    else:       # If no port are found
        #print('EV3 does not appear to be open on any /dev/rfcomm port')
        return None, None
        #sys.exit()
    
def getUserInput():
#Ask the user for input and return the UPPER case scrubbed string
    
    cmd = input('Enter Command? ')
    cmdUpper = cmd.upper()
    return cmdUpper


        
