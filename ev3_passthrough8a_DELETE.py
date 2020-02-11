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

This version (3 to 5) is the first attempt to put in a user text interface from which this can take both text commnads from the user as well as
take the voice commands coming from the GOOGLE AIY VOICE.  The first step is to make the tasks that read the file into a standalone thread.
Version 6-7 takes the loop that reads the file and sends commands to the EV3 and breaks it into (1) read file
(2) add to command queue (3) send commands from command queue to the EV3 (as a separate thread).  Version 7 is the same as 6c.
Version 8 adds a user command box from which the user can add commands to the global cmd_q, and these are multiplexed with the
command being added by the Google AIY voice interface.
"""

import serial
import time
import datetime
##import struct
import os
import sys
import ev3_rpi_ctrl_pkg
import threading
import Queue

def poll_cmd_file(ev3_cmd_filename, wait_period):
    """
    This function repeated checks the command file ev3_cmd_filename that is created by the AIY Voice program and checks if it has anything
    in it.  If it does, it send the commnand to the ev3 over the bluetooth interface.  It ends when it is  interupted by the user
    """
    print('ENTERED poll_cmd_file with name = {} wait_period = {}'.format(ev3_cmd_filename,wait_period))
    
    while True:
        
        do_sleep = False
        
        try:
            ev3_file = open(ev3_cmd_filename, "r")
        except IOError:
            do_sleep = True              # and try again   
        except KeyboardInterrupt:
            break
        
        if do_sleep:
            try:
                time.sleep(wait_period)                      # Wait for the file to be created
                continue
            except KeyboardInterrupt:
                break
                
        
        cmds = ev3_file.read().splitlines()              # get all commands and remove the line terminatorsd  (\n)
        
        for cmd in cmds:                                 # Put all commands on the global commanbd queue
            cmd_q.put(cmd)
            print('-> PUT {} ON COMMAND QUEUE'.format(cmd))
            if cmd == "STOPEV3":
                return                                    # return from thread
         
        if ev3_file is not None:
            os.remove(ev3_cmd_filename)                      # Delete processed commands so that voice_assist_ev3_ctrl can make more 
    
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
            
        cmd_q.put(cmd)                              # Add to the command/event queue for processing
        
        if cmd == "EXIT":
            return                                  # We're done if the user give "EXIT"
        
    
def send_cmds_to_ev3(ev3):
    """
    This function reads the global command queue cmd_q and sends each of the command to the EV3 with
    an appropriate delay between them.  The param ev3 is the pointer to the EV3.
    This is meant to be run as a thread
    """
    inter_cmd_wait = 2                       # Sec.  Min delay between successive commands
    
    print('ENTERED send_cmds_to_ev3 function/thread, cmd_q length is {}',format(cmd_q.qsize()))
    
    while True:
        
        try:
            cmd = cmd_q.get()                   # This should block the thread if the queue is empty
            print("-> Command from file is {}".format(cmd))
            m = ev3_rpi_ctrl_pkg.messageGuin("EV3-CMD",cmd,"text")  #  convert message; select EV3-CMD block to send to
            print('Sending to EV3 msg: {}'.format(cmd))
            ev3_rpi_ctrl_pkg.messageSend(ev3, m) # send converted message

            if cmd=="STOPEV3":
                ev3.close()
                return                                 #Thread terminates
            else:
                time.sleep(inter_cmd_wait)           # wait some time until the next commad can be sent
            
        except KeyboardInterrupt:
            break
             
    

def main():
    global cmd_q                        # global command queue.  THis is the command queue
                                                         # tga the Command_Poll threads will read command into

    
    ev3_cmd_filename = '/home/pi/Lego_ev3/ev3_cmds.txt'  # Command destined for the EV3 should be written here by voice_assist_ev3_ctrlx.py
    wait_period = 0.25                                   # SEC.  This is the amount of time to wait for the voice_assist_ev3_ctrlx to creat a file
    
    ev3, ev3PortOpen = ev3_rpi_ctrl_pkg.openEv3()               #Port poitner abd ID if successful, None otherwise

    if ev3PortOpen is not None:
        print('\nOpened EV3 Brick on {}'.format(ev3PortOpen))
                 # Get the pointer to the open BT interface
    else:       # If no port are found
        
        print('EV3 does not appear to be open on any /dev/rfcomm port')
        sys.exit()
 
##    poll_cmd_file(ev3, ev3_cmd_filename, wait_period)           # Look for commands in command file and send to EV3
    
    cmd_q = Queue.Queue()                           # THis is the command queue tga the Command_Poll threads will read command into
    
    ## THIS IS TEMP FOR DEBUGGING.  MAKE THIS A CONCURRENT THREAD
##    enter_user_cmds()
    
##    ## *** FOR DEGUGGING ONLY DONT START THREAD
##    poll_cmd_thr = threading.Thread(target=poll_cmd_file, name='Command_Poll', args=(ev3_cmd_filename, wait_period))
##    print('STARTING Command_Poll thread')
##    poll_cmd_thr.start()
##    print('JOINING Command_Poll thread')
##    poll_cmd_thr.join()
    
##    print('ENDED Command_Poll thread')
    
    send_cmd_thr = threading.Thread(target=send_cmds_to_ev3, name='Send_Cmds_to_EV3', args=(ev3,))  # Thread waits for command in cmd_q and sends to EV3
    print('STARTING Send_Cmds_to_EV3 thread')
    send_cmd_thr.start()
    
    user_cmd_thr = threading.Thread(target=enter_user_cmds, name="User_Cmd_Thread")                 # Thead allows user to enter commands
    user_cmd_thr.start()
    
    print('JOINING Send_Cmds_to_EV3 thread')
    send_cmd_thr.join()
    
    print('COMMAND QUEUE HAS {} ITEMS.  ITEMS ARE:'.format(cmd_q.qsize()))
    for i in range(cmd_q.qsize()):
          c = cmd_q.get()
          print("ITEM {}: {}".format(i,c))
          

    print('ENDED Main thread')
    
    sys.exit()
                


if __name__ == "__main__":
    main() 