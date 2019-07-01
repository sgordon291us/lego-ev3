#! /usr/bin/env python
# import packages
import serial
import time
import datetime
import struct
import os

EV3 = serial.Serial('/dev/rfcomm0')

#Debugging
print('End device name = ',EV3.name)
print('Baud rate = ', EV3.baudrate)

timeLastRx = datetime.datetime.now()
print "Local Time Now ", timeLastRx

RxToPeriod = 5      #Seconds.  This is the amount of time that can pass before doing a buffer reset


while 1:
        if EV3.inWaiting() >= 2: # check for ev3 message
            # Get the number of bytes in this message
            s = EV3.read(2)
            # struct.unpack returns a tuple unpack using []
            
            [numberOfBytes] = struct.unpack("<H", s)
            print numberOfBytes,
            # Wait for the message to complete
            while EV3.inWaiting() < numberOfBytes:
                time.sleep(0.01)
            #read number of bytes
            s = s + EV3.read(numberOfBytes)
            s = s[6:]
            # Get the mailboxName
            mailboxNameLength = ord(s[0])
            mailboxName = s[1:1+mailboxNameLength-1]
            print mailboxName,
            s = s[mailboxNameLength+1: ]
            # Get the message text
            [messageLength] = struct.unpack("<H", s[0:2])
            message = s[2:2+messageLength]
            print message
            timeLastRx = datetime.datetime.now()
            if 'hi' in message:
                print "Hello EV3"
        else:
            # See if a buffer reset is needede
            timeNow = datetime.datetime.now()
            timeSinceLastRx = timeNow - timeLastRx
            #secSinceLastRx = timeSinceLastRx.second + timeSinceLastRx.microsecond/1000000
            secSinceLastRx = timeSinceLastRx.total_seconds()
            # print "Time Since Last Rx: ", timeSinceLastRx
            if secSinceLastRx > RxToPeriod:
                EV3.flushInput
                timeLastRx = timeNow                   # Prevents repetitive flushing
                print("*** Flushed at ",timeNow)
            # No data is ready to be processed yield control to system
            time.sleep(0.01)
