#!/usr/bin/env python3
"""
This program allows the user to add command to the command file to be sent to the lego EV3.  The file is
ev3_cmd_filename, and will be created if it does not exist. The commands in the command file should be sent
to the EV3 with ev3_passthroughx.py, which should be able to run in the background.
Version 2 works somewhat in that when you first run ev3_passthrough14.py as a background process, this can send commands
to it.  This seems to work properly wiuth ev3_passthrough14.py and ev3_passthrough15.py.
Version 3 tries to (1) create an input history so that the user can scroll through it for the command entry and (2) respond to up-arrow and
down-arrow commands to use an old command.  Only (1) was implemented and it works.
Version 4 tries to implement (2).
Version 4_exp2 tries to use the getch package to read individual characters
Version 5 creates a separate procudure to handle the user input use the "history" list.  This wasnt my
preference to create this, but I can find no way to write the code so input() works will while
using the "keyboard" package.  This did not work and is being abandoned.
"""
import serial
import time
import datetime
##import struct
import os
import sys
import keyboard as kb
# import getch

def spec_input(prompt, hist_list):
    '''
This procedure prompts the user with "prompt", and reads characters until <enter>.  It also
recognizes the arrow keys and in response, allows the user to scroll through the history and select or edit
one of them.  The return value is the user input (either by typing or history lisy)
'''
    
    spec_keys = ['up','down','right','left','esc','enter','delete','backspace']
    
    spec_key = True
    user_inp = ''
    hist_dx = len(hist_list)                           #Pointer to history entr to display

#     print(prompt, end='')

    print(prompt)
    
    while spec_key:
    
        key = kb.read_key()                             #This triggers/unblocks on the downpress of any key
        next = kb.read_event()                          #Finish thge keypress--wait for release of key    
       
#             print('\n\n*** YOU PRESSED "{}"; ASCII = {}\n'.format(key,ord(key)))
#             print('\n\n*** YOU PRESSED "{}, LENGTH = {}"\n'.format(key, len(key)))
        
        if key == "enter":
            user_inp = user_inp+key
        else:
            spec_key = key in spec_keys
            
        if not spec_key:
            continue
        elif key == "up": 
            hist_dx = maximum(0,hist_dx-1)               #Decement with 0 as min
            user_inp = hist_list[hist_dx]
        elif key == "down":            
            hist_dx = minimum(len(hist_list),hist_dx+1)  #Decement with 0 as min
            user_inp = hist_list[hist_dx]                
        elif key == "left":
            pass                                        #Not implemented yet    
        elif key == "right":
            pass                                        #Not implemented yet
        elif key == "esc":
            pass                                        #Not implemented yet
        elif key == "delete":
            pass                                        #Not implemented yet
        elif key == "backspace":
            pass                                        #Not implemented yet
        else:
            pass                                        #Not implemented yet

    
#     hist_list.append(user_inp)
    
    return(user_inp)
    


def main():
    
    INPUT_HISTORY_MAX = 3                                #Max length of input history buffer
    
    ev3_cmd_filename = '/home/pi/Lego_ev3/ev3_cmds.txt'  # Command destined for the EV3 should be written here by voice_assist_ev3_ctrlx.py
#     ev3_cmd_filename_test = '/home/pi/Lego_ev3/ev3_cmds_test.txt'  # Command destined for the EV3 should be written here by voice_assist_ev3_ctrlx.py

#     wait_period = 0.25                                   # SEC.  This is the amount of time to wait for the voice_assist_ev3_ctrlx to creat a file

#     try:
#         ev3_file = open(ev3_cmd_filename, "a")     # Get ready to add user command to the end of the file
#     except IOError:
#         do_sleep = True              # and try again   
#     except KeyboardInterrupt:
#         break


    input_history = []
#     key = None
    

    
    while True:                                            #Repeatedly ask user for a command
        
        cmd = spec_input('EV3 Command? ',input_history)
        
        print('*** COMMAND = "{}"; LENGTH = {}\n'.format(cmd,len(cmd)))
        
        input_history.append(cmd)                  # Add next commannd to list
        print('-> Length of input history = {}; input_history_max = {}'.format(len(input_history), INPUT_HISTORY_MAX))
        print('-> Input history {}'.format(input_history))     #FOR DEBUGGING--DELETE
                   
        if len(input_history) > INPUT_HISTORY_MAX:
            print('-> Length of input history is {}'.format(len(input_history)))
            input_history = input_history[-INPUT_HISTORY_MAX:]       #Perform truncation to a limit of input_history_max items
            #len(input_history)-input_history_max:input_history_max
            print('-> Input history truncated to {}'.format(input_history))     #FOR DEBUGGING--DELETE
        
        try:

            ev3_file = open(ev3_cmd_filename, "a")     # Get ready to add user command to the end of the file.
            
            if cmd == "EXIT":                          #EXIT gets "intecepted" and STOPEV3 gets added before as an aid to the
                  ev3_file.write('STOPEV3\n')            #user to turn the EV3 off
            
            ev3_file.write('{}\n'.format(cmd))                    #write the command to the file, including EXIT command
            
            if ev3_file is not None:
                ev3_file.close()
                
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