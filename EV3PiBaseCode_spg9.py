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


def main():
    EV3 = serial.Serial('/dev/rfcomm5',timeout=1)   
    printSerIntInfo(EV3)
    
 


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