#!/usr/bin/env python2
"""
This program is meant to run as a background process.  It works with voice_assist_ev3_ctrlx.py.  The
voice assist program reads the users voice for commands to control the EV3, and records the user's
commands to a file.  This program continously reads the file and send the commands to the EV3.  The reason
that we need this is that the MUST be run with python3 because of the google AIY software; however, the
serial package only seems to work correctly with unicode (as the EV3 needs) when it is run as python2.
Note the shebang above that is python2.
SPG 7.7.19:  This ev3_passthrough1.py works a little with  voice_assist_ev3_ctrl9. The first time that "ev3 forward" is spoken this sends the command
to the EV3.  But the successivce "ev3 forward" commannd do not work
"""

import serial
import time
import datetime
##import struct
import os
import sys
import ev3_rpi_ctrl_pkg

def main():
    
    ev3_cmd_filename = '/home/pi/Lego_ev3/ev3_cmds.txt'  # Command destined for the EV3 should be written here by voice_assist_ev3_ctrlx.py
    wait_period = 0.25                                   # SEC.  This is the amount of time to wait for the voice_assist_ev3_ctrlx to creat a file
    
    ev3, ev3PortOpen = ev3_rpi_ctrl_pkg.openEv3()               #Port poitner abd ID if successful, None otherwise

    if ev3PortOpen is not None:
        print('\nOpened EV3 Brick on {}'.format(ev3PortOpen))
                 # Get the pointer to the open BT interface
    else:       # If no port are found
        
        print('EV3 does not appear to be open on any /dev/rfcomm port')
        sys.exit()
 
    while True:
        
        try:
            ev3_file = open(ev3_cmd_filename, "r")
        except IOError:
            time.sleep(wait_period)                      # Wait for the file to be created
            continue                                     # and try again
        
        cmds = ev3_file.read().splitlines()              # get all commands and remove the line terminatorsd  (\n)
        
        try:
            
            for cmd in cmds:
                print("-> Command from file is {}".format(cmd))
                if cmd is not None:
                    m = ev3_rpi_ctrl_pkg.messageGuin("EV3-CMD",cmd,"text")  #  convert message; select EV3-CMD block to send to
                    print('Sending to EV3 msg: {}'.format(cmd))
                    ev3_rpi_ctrl_pkg.messageSend(ev3, m) # send converted message
                    time.sleep(3)                          # DELETE--FOR DEBUGGING ONLY
                    
        except KeyboardInterrupt:
            break
        
    
        if ev3_file is not None:
            ev3.close()
            os.remove(ev3_cmd_filename)                      # Delete processed commands so that voice_assist_ev3_ctrl can make more 
    
    sys.exit()
                


if __name__ == "__main__":
    main() 