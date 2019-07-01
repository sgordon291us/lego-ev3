#!/usr/bin/env python
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


        #Tryt to reopen port because the BT message just caused the

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
    
    while True:
        
        userCmd = "FWD"
##        userCmd = input('Command? ')
        print('** COMMAND IS {}'.format(userCmd))
        userCmdUpper = userCmd.upper()
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