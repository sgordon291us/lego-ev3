#!/usr/bin/env python2
"""
This program is NOT meant to run as a background process.  It works with voice_assist_ev3_ctrlx.py.  The
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
Version 9 is an attempt to make user input respond to ctrl c and give the user a way of terminating the profgram
with ctrl c.  This should kill the assocated threads too.  (Note that SHIFT-CTRL-\ should terminate the script).
Version 9 appears to work right.  The global var "thread_stop" was used to have the subordinate threads terminate
themselves.  However, rewriting the threads a classes and having them take a STOP semafore would be the better way.
In addition, with version 9, I'm able to take commands simultaneousely with the AIY Voice program (voice_assist_ev3_ctrl10)
and the command box in ev3_passthrough9.  However, one bug remains.  When the AIY Voice program is used, for some
reason the main thread in ev3_passthrough9 cannot shut down.  I don't know why this problem is happening, but it may
be because ev3_passthrough cannot delete the ev3_cmds.txt file.
Version 10 tries to address why the program hands (does not exit) when the EXIT command it given.  The procedure send_cmds_to_ev3
was changed to put a limit on the wait time in the cmd_q.get() and catch exception Queue.Empty.  But there may be a problem with the
FASTER command.  IT does not seem to get the robot to full speed. ALso, this has not been checked with voice_assist_ev3_ctrl18.py.
Version 11 implements 'EXIT' in poll_cmd_file to terminate all threads and end the ev3_passthrough11.py proceess/prgram.  In addition, the user
input part enter_user_commands() is removed and made a different program.  This might work, but needs more testing.  However, there should be a
basic change to remove the cmd_q structure and use only the file as the command queue.  This will allow separate, multiple processes to
generate command all have ev3_passthrough send them to the ev3.
Version 12 deals the bug in poll_cmd_file() when the EXIT command is given by the user.  The fix in poll_cmd_file() succeeded.
Version 13 gets rid of the user interface/prompt in enter_user_commands().  This will have to be done by a separate python progam
and moved to Python3.  This seems to work as a foreground process and somewhat as a background process,
but has a problem.  Even after the EXIT command is processed by send_cmds_to_ev3(), and that thread shuts down
the poll_cmd_file() thread does not appear to shut down. I know this because after I feed it (copy) a command file to ev3_cmds.txt
that has EXIT at the end, then do it a second time, on the second time the poll_cmd_file() thread adds the new commands to the
cmd_q but it is not sent to the ev3 robot.  In addition, the OS process is not terminate.  You have to find another way to
properly terminate the threads in python 2.
Version14 fixed the processing of the STOPEV3 and EXIT command so it works right with ev3_user_console2.py.   The problem was processing the STOPEV3 command in send_cmds_to_ev3().  But the better way of havinbg send_cmds_to_ev3()
signal poll_cmd_file() to terminate itself is to use the event object in the threading package.  Note that this uses the global thread_stop
variable to send a signal from the send_cmds_to_ev3() to poll_cmd_file() to end.  The better "right" way of doing this is to use the event() object
in the threading package to send the signal.
Version 15 is an attempt to replace the global thread_stop variable with an event() from the threading package to perform the shutdown. This appearsa
to work properly.
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

# thread_stop = False                   # This may not be needed to make thread_stop global in scope

def poll_cmd_file(ev3_cmd_filename, wait_period, ex_event):
    """
    This function repeated checks the command file ev3_cmd_filename that is created by the AIY Voice program and checks if it has anything
    in it.  If it does, it send the commnand to the ev3 over the bluetooth interface.  It ends when "ex_event" is set
    """
    
#     global thread_stop
    print('ENTERED poll_cmd_file with name = {} wait_period = {}'.format(ev3_cmd_filename,wait_period))
    
    interval = 0                       #DELETe--for debugging
    
    while not ex_event.is_set():
        
        interval += 1                                                                                   #DELETe--for debugging
#         print('-> IN poll_cmd_file(), interval = {}   thread_stop = {}'.format(interval,thread_stop))   #DELETe--for debugging
        
        do_sleep = False
        
        ev3_file = None                 #Maybe delete this.  THis is to deal with an error on "if ev3_file is not None"
            
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
            
#             if cmd.upper() == "EXIT":
#                 thread_stop = True                       # Stop all threads (poll_cmd_file, send_cmds_to_ev3).  Should also terminate this program
#                 print('IN poll_cmd_file with name, received EXIT signal')
#                 break
            
            cmd_q.put(cmd.upper())
            print('-> PUT {} ON COMMAND QUEUE'.format(cmd))
#             if cmd == "STOPEV3":
#                 break                                    # gracefully exit and return from thread
# Above is not neeeded.  This thread will be terminate by the EXIT command detected by send_cmds_to_ev3() thread
##                return                                    # return from thread
         
        if ev3_file is not None:
            os.remove(ev3_cmd_filename)                      # Delete processed commands so that voice_assist_ev3_ctrl can make more 
        
    print('EXITED poll_cmd_file')
    
    return                                               # return and terminate thread

        
    
def send_cmds_to_ev3(ev3, ex_event):
    """
    This function reads the global command queue cmd_q and sends each of the command to the EV3 with
    an appropriate delay between them.  The param ev3 is the pointer to the EV3.
    This is meant to be run as a thread.  The ex_event parameter is an event() object in the threading package
    that allows this thread to shut down the other threads when it processes the EXIT command.
    """
#     global thread_stop
    inter_cmd_wait = 2                       # Sec.  Min delay between successive commands
    
    print('ENTERED send_cmds_to_ev3 function/thread, cmd_q length is {}',format(cmd_q.qsize()))
    
    while not ex_event.is_set():
        
        try:
            cmd = cmd_q.get(block=True, timeout=inter_cmd_wait)                   # This should block the thread if the queue is empty
            print("-> Command from file is {}".format(cmd))
            
            if len(cmd) == 0 or cmd.isspace():   # Skip commands that are blank or only whitespace
                continue
            
            if cmd == "EXIT":
#                 thread_stop = True                 # Stop all threads and allow the program to exit
                ex_event.set()                     #Sets the ex_event to signal other threads to shut themselves down
                print("-> FROM send_cmds_to_ev3, processing EXIT, thread_stop = {}".format(ex_event.is_set()))
                break                              # Close the open file and end the thread

            m = ev3_rpi_ctrl_pkg.messageGuin("EV3-CMD",cmd,"text")  #  convert message; select EV3-CMD block to send to
#             print('Sending to EV3 msg: {}'.format(cmd))
            ev3_rpi_ctrl_pkg.messageSend(ev3, m) # send converted message

#             if cmd=="STOPEV3":
#                 break                               # thread terminates gracefully
##                ev3.close()
##                return                                 #Thread terminates
#             else:
#                 time.sleep(inter_cmd_wait)           # wait some time until the next commad can be sent
# The command STOPEV3 should not terminate the thread

            time.sleep(inter_cmd_wait)           # wait some time until the next commad can be sent
            
        except KeyboardInterrupt:
            break
        
        except Queue.Empty as e:
#             print('FROM send_cmds_to_ev3, EXCEPTION IS {}'.format(e))
            continue
        
    ev3.close()
    
    print('EXITED send_cmds_to_ev3')
    return
    
             
    

def main():
    global cmd_q                        # global command queue.  THis is the command queue
                                                         # tga the Command_Poll threads will read command in
#     global thread_stop                  # This is a signal to the threads to stop themselves.  This is a bad way of
                                        # sending this signal because it forces the threads to use common memory.  The
                                        # better way is to convert the threads to real classes and send in a semafore
                                        # requesting a stop
                                                
#     thread_stop = False                 # Initially, allow all subordinate threads to run
    
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
    
    exit_event = threading.Event()                  #This is the event that will signal thread to shut themselves down
    
    poll_cmd_thr = threading.Thread(target=poll_cmd_file, name='Command_Poll', args=(ev3_cmd_filename, wait_period, exit_event))
    print('STARTING Command_Poll thread')
    poll_cmd_thr.start()
##    print('JOINING Command_Poll thread')
#     poll_cmd_thr.join()
    
##    print('ENDED Command_Poll thread')
    
    send_cmd_thr = threading.Thread(target=send_cmds_to_ev3, name='Send_Cmds_to_EV3', args=(ev3,exit_event))  # Thread waits for command in cmd_q and sends to EV3
    print('STARTING Send_Cmds_to_EV3 thread')
    send_cmd_thr.start()
    send_cmd_thr.join()
    
#     user_cmd_thr = threading.Thread(target=enter_user_cmds, name='Enter_User_Cmds')                 # Thread allows the user to enter commands throuhg the console
#     user_cmd_thr.start()                                                                            
#     user_cmd_thr.join()                                                                             # Dont start these user_cmd_thr threads.  This will be done by a separate Python program
#     enter_user_cmds()                       # Allow user to enter commands
#     thread_stop = True                      # stop all other thread so that main thread can exit
    
    # When the user exits the command session, terminate the threads
##    poll_cmd_thr._stop()
##    send_cmd_thr._stop()
    
    
##    user_cmd_thr = threading.Thread(target=enter_user_cmds, name="User_Cmd_Thread")                 # Thead allows user to enter commands
##    user_cmd_thr.start()
    
##    print('JOINING Send_Cmds_to_EV3 thread')
##    send_cmd_thr.join()
##    
##    print('COMMAND QUEUE HAS {} ITEMS.  ITEMS ARE:'.format(cmd_q.qsize()))
##    for i in range(cmd_q.qsize()):
##          c = cmd_q.get()
##          print("ITEM {}: {}".format(i,c))
          

    print('ENDED Main thread')
    
    sys.exit()
    
    return
                


if __name__ == "__main__":
    main() 