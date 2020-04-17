#!/usr/bin/env python3
"""
This program allows the user to add command to the command file to be sent to the lego EV3.  The file is
ev3_cmd_filename, and will be created if it does not exist. The commands in the command file should be sent
to the EV3 with ev3_passthroughx.py, which should be able to run in the background.
"""
import serial
import time
import datetime
##import struct
import os
import sys


def enter_user_cmds():
    """
    Allow user to enter command that get added to the global cmd_q.  These commands get thrown into the cmd_q and are multiplexed with
    the ones from the AIY voice interface.  The user is repeated asked for additional command until the user gives the "EXIT" command,
    at which point this function returns and the thread terminates.  This function is intended to be run as a thread concurrent with
    poll_cmd_file and send_cmds_to ev3.  In addition, ctrl-c will ignore the currently typed command, and two ctrl-c's is the same
    as "EXIT".
    """
    
    global cmd_q                                    # THis is the command/event queue that both the user text commands and the
                                                    # AIY voice command are put into.
    global thread_stop                              # Allows stopping of poll_cmd_file and send_cmds_to_ev3
    
    first_ctrl_c = False
    
    while True:
        
        try:
            cmd = raw_input("EV3 Command? ").upper()
            first_ctrl_c = False
            
        except KeyboardInterrupt:
            if not first_ctrl_c:                    # First time user types ^c
                first_ctrl_c = True
                print('')
                continue
            else:              
                return                              # THis is the second ctrl-c, so we're done
            
# By commenting out the code below, the EXIT command should be put on the command queue then processed by poll_cmd_file()
        if cmd == "EXIT":
            thread_stop = True                      # Stop poll_cmd_file and send_cmds_to_ev3
            return                                  # We're done if the user give "EXIT"
        
        cmd_q.put(cmd)                              # Add to the command/event queue for processing
        
    return

def main():
    
    ev3_cmd_filename = '/home/pi/Lego_ev3/ev3_cmds.txt'  # Command destined for the EV3 should be written here by voice_assist_ev3_ctrlx.py
#     wait_period = 0.25                                   # SEC.  This is the amount of time to wait for the voice_assist_ev3_ctrlx to creat a file

#     try:
#         ev3_file = open(ev3_cmd_filename, "a")     # Get ready to add user command to the end of the file
#     except IOError:
#         do_sleep = True              # and try again   
#     except KeyboardInterrupt:
#         break
    
    ev3_file = open(ev3_cmd_filename, "a")     # Get ready to add user command to the end of the file
    
    while True:
        
        try:
            cmd = input("EV3 Command? ").upper()
            ev3_file.write('{}\n'.format(cmd))                    #write the command to the file, including EXIT command
            first_ctrl_c = False
            
        except KeyboardInterrupt:
            if not first_ctrl_c:                    # First time user types ^c
                first_ctrl_c = True
                print('')
                continue
            else:              
                break                              # THis is the second ctrl-c, so we're done
            
# By commenting out the code below, the EXIT command should be put on the command queue then processed by poll_cmd_file()
        if cmd == "EXIT":
            break                                  # We're done 
        
#         cmd_q.put(cmd)                              # Add to the command/event queue for processing


if __name__ == "__main__":
    main() 