#! /usr/bin/env python
# import packages
import serial
import time
import datetime
##import deltatime
import struct
import os
import sys

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
    
    #Try resetting te port if it doesnt look like it's working
##    if EV3.inWaiting() == 0:
##        print('Trying flush')
##        EV3.flush()
##        print('EV3.inWaiting() = {}'.format(EV3.inWaiting()))
##        print('Trying input reset')
##        EV3.reset_input_buffer()
##        print('EV3.inWaiting() = {}'.format(EV3.inWaiting()))
##        print('Trying output reset')
##        EV3.reset_output_buffer()
##        print('EV3.inWaiting() = {}'.format(EV3.inWaiting()))
##        print('Trying close/open')
##        EV3.close()
##        EV3.open()
##        print('EV3.inWaiting() = {}'.format(EV3.inWaiting()))
##        print('Trying pipe_abort_read')
##        EV3.pipe_abort_read_r
##        EV3.pipe_abort_read_w
##        print('EV3.inWaiting() = {}'.format(EV3.inWaiting()))
##        print('Trying cancel_read()')
##        EV3.cancel_read()
##        print('EV3.inWaiting() = {}'.format(EV3.inWaiting()))        
        
    

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
