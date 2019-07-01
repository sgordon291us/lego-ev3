#! /usr/bin/env python
import serial
import time
EV3 = serial.Serial('/dev/rfcomm0')
print "Listening for EV3 Bluetooth messages, press CTRL C to quit."
try:
   while 1:
      n = EV3.inWaiting()
      if n <> 0:
         s = EV3.read(n)
         for n in s:
            print "%02X" % ord(n),
         print
      else:
         # No data is ready to be processed
         time.sleep(0.5)
except KeyboardInterrupt:
   pass
EV3.