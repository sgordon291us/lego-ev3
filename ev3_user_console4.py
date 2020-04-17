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
"""
import serial
import time
import datetime
##import struct
import os
import sys

# print('POINT 1')
import keyboard as kb             #This seems to get an error at runtime.  Maybe cant use keyboard package


# print('POINT 2')                  #FOR DEBUGGING--DELETE

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
#     print('POINT 3')                  #FOR DEBUGGING--DELETE  

    input_history = []
    key = None
    
#     print('POINT 4')                  #FOR DEBUGGING--DELETE   
#     print('EV3 INTRO? ',end='')
#     
#     while True:  # making a loop
#         
#         key = kb.read_key()                             #This triggers/unblocks on the downpress of any key 
# 
#         
#         if  key  is not None:
#             print('\n\n*** YOU PRESSED "{}"\n'.format(key))
#             
#             if key == "up":
#                 print('*** UP WAS PRESSED')
#             
#             if key == "down":
#                 print('*** DOWN WAS PRESSED')  
#             
#             next = kb.read_event()                      #This waits for the release of the pressed key


 
        
#         key = kb.read_key()
#         
#         if key is not None:
#             print('\n\n*** YOU PRESSED "{}"'.format(key))
#             cmd = input('<CR> to continue').upper()
        
#         key = None


        
#         try:  # used try so that if user pressed other than the given key error will not be shown
#             if kb.is_pressed('q'):  # if key 'q' is pressed 
#                 print('You Pressed A Key!')
#                 break  # finishing the loop
#         except:
#             break  
    
    while True:                                            #Repeatedly ask user for a command
        
#         print('POINT 5')                  #FOR DEBUGGING--DELETE
        
        print('EV3 Command? ',end='')
        
#         print('POINT 6')                  #FOR DEBUGGING--DELETE
        
        spec_key = True
        
        while spec_key:
        
#             print('POINT 7')                  #FOR DEBUGGING--DELETE
            key = kb.read_key()                             #This triggers/unblocks on the downpress of any key
              
#             key = keyboard.read_key()                             #This triggers/unblocks on the downpress of any key
                         
#             print('POINT 8')                  #FOR DEBUGGING--DELETE
#             if  key  is not None:
        
            print('\n\n*** YOU PRESSED "{}"\n'.format(key))
                
            if key == "up":
                print('*** UP WAS PRESSED')
                spec_key = False
            
            if key == "down":
                print('*** DOWN WAS PRESSED')
                spec_key = False
                
            if key == "esc":
                print('*** ESC WAS PRESSED')
                spec_key = False
                
#                 if key == "enter":
#                     print('*** ENTER WAS PRESSED')
            
#             else:
#                 spec_key = False
    

            next = kb.read_event()             #Finish thge keypress--wait for release of key    

        print('*** DONE WITH SPECIAL KEY READ')
#         ch = kb.is_pressed('q')
#         
#         if ch:
#             print('\n\nChar "{}" was pressed\n\n'.format(ch)) 
        
        cmd = input().upper()
        
#         cmd = input("EV3 Command? ").upper()
        
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