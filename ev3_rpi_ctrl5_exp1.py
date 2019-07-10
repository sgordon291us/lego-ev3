#!/usr/bin/env python3
#This code allows simple control of the EV3 from the RPi using a text interface.
#Based on a text command from teh user, this will send a message to the EV3 to
#perform an action.  Valid actions are:
#FORWARD, REVERSE, STOP, JOSHISCOOL
#Other commands are
#EXIT, END
#The it sould not be case-sensitiive to the input taken from the user, but the message
#send to the EV3 IS case-sensitive
# This version (4) has the critical procedures IMPORTED from teh ev3_rpi_ctrl_pkg
# Version 5 uses msg_fmt_send instead of messageGuin() and messageSenbd().
# Version 5 is an experimental version trying to convert everything to python 3.  The problem with the
# Google AIY software not working is (I think) because the AIY software have to be run with Python 3,
# but we're using python 2 routines in the PySerial packsge, including inWaiting()
import serial
import time
import datetime
import struct
import os
import sys
import ev3_rpi_ctrl_pkg


def main():
##    EV3 = serial.Serial('/dev/rfcomm5',timeout=1)   
##    printSerIntInfo(EV3)
    
    global secSinceLastRx, RxToPeriod
    
##    global EV3

    timeStart = datetime.datetime.now()
    EV3, ev3PortOpen = ev3_rpi_ctrl_pkg.openEv3()               #Port poitner abd ID if successful, None otherwise
##    ev3PortOpen = ev3Info[0]
    
    print('# Ev3PortOpen {}'.format(ev3PortOpen))

##    ev3PortOpen, EV3 = ev3_rpi_ctrl_pkg.openEv3()               #Port ID if successful, False otherwise
##    ev3PortOpen = ev3Info[0]

    if ev3PortOpen is not None:
        print('\nOpened EV3 Brick on {}'.format(ev3PortOpen))
                 # Get the pointer to the open BT interface
    else:       # If no port are found
        
        print('EV3 does not appear to be open on any /dev/rfcomm port')
        sys.exit()
 

    #Debugging
##    print('End device name = ',EV3.name)
##    print('Baud rate = ', EV3.baudrate)

    timeLastRx = datetime.datetime.now()
    print("Local Time Now {}\n".format(timeLastRx))

    RxToPeriod = 5      #Seconds.  This is the amount of time that can pass before doing a buffer reset
    maxRxWait = 4       #Max time in sec to wait for message from EV3
    
    try:
    
        while True:
            userCmd = input('Command? ')                     # REALLY NOT SURE WHAT THE PROBLEM HERE IS
            userCmdUpper = userCmd.upper().strip()               #Convert to upper ans strip all spaces
            
##            userCmdUpper = getUserInput()
##            print('** COMMAND IS {}'.format(userCmdUpper))
            
            
            if "FORWARD" == userCmdUpper or "FWD" == userCmdUpper:
                ev3Msg = "FWD"
            elif "BACK" == userCmdUpper or "BACKWARDS" == userCmdUpper or "RVS" == userCmdUpper or "REVERSE" == userCmdUpper:
                ev3Msg = "RVS"
            elif "STOP" == userCmdUpper:
                ev3Msg = "STOP"
            elif "JOSHISCOOL" == userCmdUpper:
                ev3Msg = "JOSHISCOOL"
            elif "STOPEV3" == userCmdUpper or "STOPPROGRAM" == userCmdUpper:
                ev3Msg = "STOPEV3"
            elif "EXIT" == userCmdUpper or "END" == userCmdUpper:
                break
            else:
                ev3Msg = None
                
            if ev3Msg is not None:
##                err = ev3_rpi_ctrl_pkg.msg_fmt_send(EV3, "EV3-CMD",ev3Msg,"text")
##                if err:
##                    print('*** Error sending {}, err no {}'.format(ev3Msg, err))                             
                                                    
                m = ev3_rpi_ctrl_pkg.messageGuin("EV3-CMD",ev3Msg,"text")  #  convert message; select EV3-CMD block to send to
                print('Sending to EV3 msg: {}'.format(ev3Msg))
                ev3_rpi_ctrl_pkg.messageSend(EV3, m) # send converted message
            else:
                print('** Error with {}'.format(userCmd))
                
            time.sleep(2)                                # Just slow the loop a little
                
    except KeyboardInterrupt:
        # Send a stop message and stop the robot
        ev3Msg = "STOP"
        m = ev3_rpi_ctrl_pkg.messageGuin("EV3-CMD",ev3Msg,"text")  #  convert message; select EV3-CMD block to send to
        print('Sending to EV3 msg {}'.format(ev3Msg))
        ev3_rpi_ctrl_pkg.messageSend(EV3, m) # send converted message

    
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