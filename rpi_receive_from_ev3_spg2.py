#! /usr/bin/env python
import serial
import time
import datetime

EV3 = serial.Serial('/dev/rfcomm2')
print "Listening for EV3 Bluetooth messages, press CTRL C to quit."
try:
   while 1:
       
      n = EV3.inWaiting()
##      n = EV3.in_waiting         # checking to see of using the 2.7 property works better
      if n <> 0:
         s = EV3.read(n)
         for n in s:
            print "%02X" % ord(n),
         print
      else:
         # No data is ready to be processed
         print('Sleeping, time is {}'.format(datetime.datetime.now().time()))                                                 
         time.sleep(0.5)
except KeyboardInterrupt:
   pass

EV3.close()