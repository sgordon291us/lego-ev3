#!/usr/bin/env python3
"""
The purpose of this program is to test threading and to investigate the problem of the main program
not being able to terminate
"""
# import Tkinter as tk
from tkinter import *
from tkinter import messagebox
# import tkMessageBox

import serial
import time
import datetime
##import struct
import os
import sys
# import ev3_rpi_ctrl_pkg
import threading
# import Queue



def repeat_1_sec(msg):
    """This repeats msg every 1 sec and send output to the console
    """
    
    global stop_thread_1
    

#     win1 = Tk()
#     win1.eval('tk::PlaceWindow %s ' % win1.winfo_toplevel())
#     win1.withdraw
#     
#     messagebox.showinfo('repeat_1_sec','FIRST MESSAGE')
#   
#     win1.deiconify()
#     win1.destroy()
#     win1.quit()
    
    

    
    print('ENTERED repeat_1_sec, message = {}'.format(msg))
    
    i = 1
    while not stop_thread_1:
        print('\tFROM repeat_1_sec, message {}: {}'.format(i,msg))
#         tkMessageBox.showinfo(title="FROM repeat_1_sec", message="Hello World!")
        time.sleep(1)
        
    else: 
        print('\tFROM repeat_1_sec, stopping thread')

        
    return

def repeat_3_sec(msg):
    """This repeats msg every 3 sec and send output to the console
    """
    
    global stop_thread_3
    
    print('ENTERED repeat_3_sec, message = {}'.format(msg))
    
    i = 1
    while not stop_thread_3:
        print('\tFROM repeat_3_sec, message {}: {}'.format(i,msg))
        time.sleep(3)
        
    else: 
        print('\tFROM repeat_3_sec, stopping thread')
        
    return
  
        
def user_cmds():
    """This procedure takes command from the user to control the threads
"""
    
    global stop_thread_1, stop_thread_3
    
#     done = False
#     
#     while not done:
#         cmd = input('COMMAND? ').upper()
#         if cmd == 'EXIT':
#             done = True
#         elif cmd == "START THREAD 1":
#             t1 = threading.Thread(target=repeat_1_sec, name="REPEAT 1 SEC", args=("One sec wait"))
#         elif cmd == "START THREAD 3":
#             t3 = threading.Thread(target=repeat_3_sec, name="REPEAT 3 SEC", args=("Three sec wait"))
#         elif cmd == "STOP THREAD 1":
#             stop_thread_1 = True
#         elif cmd == "STOP THREAD 3":
#             stop_thread_3 = True
#             
#     else:
#         print('FROM user_cmds(), stopping all threads')
#         stop_thread_1 = True
#         stop_thread_3 = True
#         
    return

def main():
    
    global stop_thread_1, stop_thread_3
        
    stop_thread_1 = False
    stop_thread_3 = False
    
    done = False
    
    while not done:
        cmd = input('COMMAND? ').upper()
        if cmd == 'EXIT':
            done = True
        elif cmd == "START THREAD 1":
            t1 = threading.Thread(target=repeat_1_sec, name="REPEAT 1 SEC", args=('One sec wait',))
            t1.start()
        elif cmd == "START THREAD 3":
            t3 = threading.Thread(target=repeat_3_sec, name="REPEAT 3 SEC", args=('Three sec wait',))
            t3.start()
        elif cmd == "STOP THREAD 1":
            stop_thread_1 = True
        elif cmd == "STOP THREAD 3":
            stop_thread_3 = True
        else:
            print('\nUNKNOWN CMD {}\n'.format(cmd))
            
            
#     else:
#         print('FROM user_cmds(), stopping all threads')
#         stop_thread_1 = True
#         stop_thread_3 = True
        
    
    print('ENDED Main thread')
    
    sys.exit()
    
        
if __name__ == "__main__":
    main() 



