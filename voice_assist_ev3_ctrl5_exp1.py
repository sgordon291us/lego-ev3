#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
#
# limitations under the License.
#
#SPG 6/22/19:  This uses the AIY Google voice assistant (assistant_library_with_local_commands_demo.py)
# as a starting point and generates control commands for the LEGO EV3.
#SPG: This experimental version (v5_exp1) puts the code from ev3_rpi_ctrl_pkg into the source here to
# try to circumvent the segmentation fault error when calling messageSend

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import logging
import platform
import subprocess
import sys
##import ev3_rpi_ctrl_pkg
import serial
import time
import datetime
import struct
import os

from google.assistant.library.event import EventType

from aiy.assistant import auth_helpers
from aiy.assistant.library import Assistant
from aiy.board import Board, Led
from aiy.voice import tts


def printSerIntInfo(ser):
    #print('End Device Name {}  Port = {}  Baud Rate = {}   IsOpen = {}\n  XonXoff = {}'.format(ser.name,
    #    ser.port, ser.baudrate, ser.isOpen(), ser.xonxoff))
    print(ser.get_settings())
 
##    print('Settings: {}'.format(ser.getSettingsDict()))
##    print('Num bytes in waiting = {}   isOpen = {}'.format(ser.inWaiting(), ser.isOpen()))
##    print('CD {}   CTS {}   DSR {}   RI {}'.format(ser.getCD(), ser.getCTS(), ser.getDSR(), ser.getRI()))


#create function with inputs for mailbox, message, message type (number, text, logic)
def messageGuin(boxName,message,messageType):
    print('*** messageGuin Point 0')
    mType=False
    #change message length based on type on message
    if messageType == "text":
            length = len(boxName) + len(message) + 10
            mType = True
    if messageType == "logic":
            length = len(boxName) + 12
            mType = True
    if messageType == "number":
            length = len(boxName) + 16
            mType = True
    print('*** messageGuin Point 1')
    if mType:
        # add chars to message
        print('*** messageGuin Point 2')
        btMessage = [ chr(0) for temp in range (0,length)]
        btMessage[2] = chr(1)
        btMessage[4] = chr(0x81)
        btMessage[5] = chr(0x9E)
        btMessage[6] = chr(len(boxName) + 1)
        btMessage[7:7+len(boxName)] = boxName
        payloadPointer = 8 + len(boxName)
        #add different chars based on message type
        if messageType == "text" :
                print('*** messageGuin Point 3')
                btMessage[payloadPointer] = chr((len(message) + 1) & 0xff)
                btMessage[payloadPointer + 1] = chr((len(message) + 1) >> 8)
                btMessage[payloadPointer + 2:len(message)] = message
                endPoint = payloadPointer + len(message) + 1
        if messageType == "logic" :
                btMessage[payloadPointer] = chr(2)
                btMessage[payloadPointer + 1] = chr(0)
                if message == True:
                        btMessage[payloadPointer + 2] = chr(1)
                endPoint = payloadPointer + 2
        if messageType == "number":
                btMessage[payloadPointer] = chr(4)
                btMessage[payloadPointer + 2:] = struct.pack('f',message)
                endPoint = payloadPointer + 4
        btMessage[0] = chr((endPoint & 0xff))
        btMessage[1] = chr(endPoint >> 8)
        print('*** messageGuin Point 4')
##        print('*** btmessage = {}'.format(btMessage))
##        return None                    # for debugging--DELETE
        return btMessage #output the converted message
    else: #output error message
        print('*** messageGuin Point 5')
        print("Bad Message")
        return "error"
##    print('*** Returning now...')
##    return

# FOR DEBUGGING DELETE THIS PROCEDURE
def messageSendX(d_ev3):
    print("*** EV3 Info:", d_ev3.get_settings())
    return

def messageSendY(xy):
    print("**** EV3 Message {}:",xy)
    return

def messageSend(dest_ev3, message): #make send message function
    print('**** Point 0, message = ',message)
    print('**** EV3 type',type(dest_ev3))
    print('**** EV3 name',dest_ev3.name)
    print('**** EV3 Settings: name', dest_ev3.name, dest_ev3.get_settings())
    if dest_ev3.isOpen() == True: #check if ev3 is connected
        print('**** Point 1')
        print('**** EV3 type',type(dest_ev3))
        print('**** EV3 name',dest_ev3.name)
        print('**** EV3 Settings: name', dest_ev3.name, dest_ev3.get_settings())
        for n in range(0, 2 + ord(message[0]) + (ord(message[1]) * 256 )): #run different amount of times based on the message
            print('**** Point 2; message[{}] = {}'.format(n, message[n]))
            dest_ev3.write(message[n]) #send message
    print('**** Point 3')
    return
                        
def messageRcv(srcEv3, maxWait=4):
#This procedure receies a message from the EV3.  The inputs are the EV3 interface on src_ev3 and the maximum wait
#time maxWait in seconds.  After the maxWait time, it will return with None.  The value returned is the text of the
#message from the EV3
    
    RxToPeriod = 5                               # Seconds.  This is the timeout period after which this
                                                # procedure declares the LEGO EV3 not reachable on the BT
                                                # interface.  Right now it takes no action for this situation
    
    timeStart = datetime.datetime.now()
    timeLastRx = timeStart                       # Initialize this so you dont get an error on first compare
    while (datetime.datetime.now() - timeStart).total_seconds() < maxWait:
##            print('Time {}   CD {}   CTS {}   DSR {}   RI {}   InWaiting {}'.format(datetime.datetime.now().time(), EV3.getCD(),
##                EV3.getCTS(), EV3.getDSR(), EV3.getRI(), EV3.inWaiting()))


        if srcEv3.inWaiting() >= 2: # check for ev3 message
##                print('inWaiting = {}'.format(EV3.inWaiting()))
            # Get the number of bytes in this message
            s = srcEv3.read(2)
            # struct.unpack returns a tuple unpack using []
            
            [numberOfBytes] = struct.unpack("<H", s)
##                print numberOfBytes,
            # Wait for the message to complete
##                print("{}   Expecting num of bytes {}".format(datetime.datetime.now().time(), numberOfBytes))
            while srcEv3.inWaiting() < numberOfBytes:
##                print("Waiting at point 1")
##                print("Expecting num of bytes {}".format(numberOfBytes))
                time.sleep(0.01)
            #read number of bytes
            s = s + srcEv3.read(numberOfBytes)
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
#                print message
##                timeLastRx = datetime.datetime.now()
##                if 'hi' in message:
##                    print "Hello EV3"
        elif srcEv3.inWaiting() == 1:
            # The message is only partially received, so wait a little longer
##            print('inWaiting = 1;  timenow is {}'.format(datetime.datetime.now().time()))
##                printSerIntInfo(EV3)
            time.sleep(0.01)
        else:
            # Nothing was received, so either wait for another period or perform
            # a buffer clear or reset, if desired
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
##                reset_bt_if()
            # No data is ready to be processed yield control to system
            time.sleep(0.01)
    else:
        return None
                
def reset_bt_if():
    #Bluetooth interface reset
    
    global EV3
    
    m = messageGuin("BT","Fr RPi BT CLEAR","text")  #  convert message; message instructs EV3 to clear BT interface
    print('** Sending EV3 BT CLEAR ')
    messageSend(EV3, m) # send converted message
    time.sleep(7.0)            # wait 5 sec between messages.  This was found
                        #experimentally to be the approx the lowest delay that
                        #the EV3 and RPi can deal with
    ev3PortOpen = openEv3()               #Tryt to reopen port because the BT message just caused the

def openEv3():
#This procedure runs through the /dev/rfcommx ports starting at 0 and going up to 100.  It will open
#try each rfcommx port and open the first one that is successful.  It will return the pointer to the EV3
#     port in text
# and the pointer to the EV#if it is successful.  If not successful, it returns False

##    global EV3
    
    ev3PortBase = '/dev/rfcomm'
    # a number will be appended to try to open it.  This is supposed to be the bluetooth port

    for n in range(0,100):
        ev3Port = ev3PortBase + str(n)
    ##        print('Trying port {}'.format(ev3Port))
        try:
            local_EV3 = serial.Serial(ev3Port)
        except serial.SerialException:
            continue
        else:
            print('****** Opened EV3 Brick on {}'.format(ev3Port))
            print('****** EV3 type',type(local_EV3))
            print('****** EV3 name',local_EV3.name)
            return local_EV3, ev3Port
            break
    else:       # If no port are found
        #print('EV3 does not appear to be open on any /dev/rfcomm port')
        return None, None
        #sys.exit()
    
def getUserInput():
#Ask the user for input and return the UPPER case scrubbed string
    
    cmd = raw_input('Enter Command? ')
    cmdUpper = cmd.upper()
    return cmdUpper



def power_off_pi():
    tts.say('Good bye!')
    subprocess.call('sudo shutdown now', shell=True)


def reboot_pi():
    tts.say('See you in a bit!')
    subprocess.call('sudo reboot', shell=True)


def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    tts.say('My IP address is %s' % ip_address.decode('utf-8'))
    
def exit_pi():
# This is for a local command to exit the voice control program
    tts.say('Ending voice control')
##    sys.exit()

def open_connected_ev3():
# This opens the LEGO EV3 on the bluetooth (BT) interface.  Note that the BT interface must be on and
# paired with the LEGO EV3 for this to work.  Function returns the pointer to the serial BT interface
# (if successful) or None if not successful
##    print('** ENTERED open_connected_ev3')
    EV3, ev3PortOpen = ev3_rpi_ctrl_pkg.openEv3()               #Port ID if successful, False otherwise
##    print('** PERFORMED ev3_rpi_ctrl_pkg.openEv3')
##    print('\n-> Ev3PortOpen {}\n'.format(ev3PortOpen))

    if ev3PortOpen is not None:
        print('\n-> Opened EV3 Brick on {}'.format(ev3PortOpen))   # Get the pointer to the open BT interface
        print('*** EV3 type',type(EV3))
        print('\n-> EV3 Settings: name', EV3.name, EV3.get_settings())
        print('*** Returning from open_connected_ev3()')
        return EV3, ev3PortOpen
    else:       # If no port are found
        print('\n** EV3 does not appear to be open on any /dev/rfcomm port\n')
        tts.say('EV3 does not appear to be open on any /dev/rfcomm port')
        print('*** Returning from open_connected_ev3()')
        return None, None

def process_event(assistant, led, event):
# Function returns a Boolean.  True means user asked the conversation to end; false otherwise

    global EV3                             # THis is the pointer to the LEGO EV3

    logging.info(event)
    if event.type == EventType.ON_START_FINISHED:
        led.state = Led.BEACON_DARK  # Ready.
        print('Say "OK, Google" then speak, or press Ctrl+C to quit...')
    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        led.state = Led.ON  # Listening.
    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print('You said:', event.args['text'])
        text = event.args['text'].lower()
        if text == 'power off':
            assistant.stop_conversation()
            power_off_pi()
        elif text == 'reboot':
            assistant.stop_conversation()
            reboot_pi()
        elif text == 'ip address':
            assistant.stop_conversation()
            say_ip()
        elif text == 'ev3 forward' or text == 'lego forward':
            ev3Msg = "FWD"
            print('*** ENTERING messageGuin')
            m = ev3_rpi_ctrl_pkg.messageGuin("EV3-CMD", ev3Msg,"text")  #  convert message; select EV3-CMD block to send to
##            print('*** EV3 is {}; EV3.isOpen() is {}'.format(EV3))
##            print('*** EV3.isOpen() is {}'.format(EV3.isOpen()))
            print('*** After messageGuin() \n *** Enter messageSendX')
            print('-> EV3 Settings', EV3.get_settings())
##            ev3_rpi_ctrl_pkg.messageSendX(EV3)   # DELETE FOR DEBUGGING
##            print('*** Enter messageSendY')
##            ev3_rpi_ctrl_pkg.messageSendY(m)     # DELETE FOR DEBUGGING
##            ev3_rpi_ctrl_pkg.messageSend(EV3, m) # send converted message # DUPLICXATE OF BELOW
            if EV3 is not None and EV3.isOpen() is True:
                print('\n -> Sending to EV3 msg: {} \n'.format(ev3Msg))
                print('*** ENTERING messageSend')
                ev3_rpi_ctrl_pkg.messageSend(EV3, m) # send converted message
            else:
                print("\n  Can't send--EV3 is not open \n")
        elif text == 'ev3 open' or text == 'open ev3' or text == 'open lego' or text == 'lego open':
            EV3, ev3Port = open_connected_ev3()                 # Try to open the EV3
            print('**** Returned from open_connected_ev3()')
            if EV3 is not None:
                tts.say('EV3 has been opened')
                print('**** EV3 type',type(EV3))
                print('**** EV3 name',EV3.name)
                print('-> EV3 Settings', EV3.get_settings())
            else:
                tts.say('EV3 has not been opened')
        elif text == 'exit':
            assistant.stop_conversation()
            exit_pi()
            return True                     # Indicate that user asked that the conversation end
            
    elif event.type == EventType.ON_END_OF_UTTERANCE:
        led.state = Led.PULSE_QUICK  # Thinking.
    elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED
          or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
          or event.type == EventType.ON_NO_RESPONSE):
        led.state = Led.BEACON_DARK  # Ready.
    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)

    return False                                  # User DID NOT ask for conversation to end


def main():
    
    global EV3                                    # THis is the pointer to the LEGO EV3.  This is a declared
                                                  # as global so that during multiple calls to process_event,
                                                  # the pointer in EV3 will have a persistant value
    
    EV3 = None
    
    logging.basicConfig(level=logging.INFO)

    credentials = auth_helpers.get_assistant_credentials()
    with Board() as board, Assistant(credentials) as assistant:
        for event in assistant.start():
            exit_conv = process_event(assistant, board.led, event)
            if exit_conv:                         
                break                           # Stop this look if user requested it
            
#    sys.exit()          # For some reason this generates a segmentation fault

if __name__ == '__main__':
    main()
