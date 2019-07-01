#! /usr/bin/env python
# import packages
import serial
import time
import datetime
##import deltatime
import struct
import os

def main():

        timeStart = datetime.datetime.now()
        EV3 = serial.Serial('/dev/rfcomm3')


        
        while 1:
            
                timeFromStart = datetime.datetime.now() - timeStart
##                print('Time {}   inWaiting  {} cts {}   dsr {}   dsrdtr {}   fd {}   CD {}   CTS {}   DSR {}   RI {}'.format(timeFromStart,EV3.inWaiting(),
##                    EV3.cts, EV3.dsr, EV3.dsrdtr, EV3.fd, EV3.getCD(), EV3.getCTS(), EV3.getDSR(), EV3.getRI()))

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


if __name__ == "__main__":
    main()
