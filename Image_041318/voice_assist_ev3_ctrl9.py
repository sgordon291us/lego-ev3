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
# limitations under the License.
#
# SPG 6/22/19:  This uses the AIY Google voice assistant (assistant_library_with_local_commands_demo.py)
# as a starting point and generates control commands for the LEGO EV3.
#SPG 7/3/19: Note that this should  be the same/equivalent code to the v5 version, EXCEPT THAT IT STARTED WITH
# ASSISTANT_LIBRARY_WITH_LOCAL_COMMANDS DEDO FROM THE 4/13/18 image of the AIY OS.
# Version 9 uses ev3_passtroughx to send commandfs to the EV3.  The reason that they are two separate programs is that this progam
# has to run as python3 and the serial package has to run as python2
# SPG 7.7.19:  This version (9) works a little.  The first time that "ev3 forward" is spoken this sends the command
# to the EV3.  But the successivce "ev3 forward" commannd do not work

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import logging
import platform
import subprocess
import sys
import time
import ev3_rpi_ctrl_pkg

import aiy.assistant.auth_helpers
from aiy.assistant.library import Assistant
import aiy.audio
import aiy.voicehat
from google.assistant.library.event import EventType

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)


def power_off_pi():
    aiy.audio.say('Good bye!')
    subprocess.call('sudo shutdown now', shell=True)


def reboot_pi():
    aiy.audio.say('See you in a bit!')
    subprocess.call('sudo reboot', shell=True)


def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))


def exit_pi():
    # This is for a local command to exit the voice control program
    aiy.audio.say('Ending voice control')
    ##    sys.exit()
def send_to_ev3(message):
    """
THis takes the "message" and appends it to the file that is read by the ev3_passthoughx.py program.  THat program
formats it and send to the EV3 brick.
"""
    ev3_cmd_filename = '/home/pi/Lego_ev3/ev3_cmds.txt'  # Command destined for the EV3 should be written here by voice_assist_ev3_ctrlx.py
    wait_period = 0.25                                   # SEC.  This is the amount of time to wait for the voice_assist_ev3_ctrlx to creat a file

# Open command file, but we may have to wait if it's in use by ev3_passthoughx

    while True:
        try:
            ev3_file = open(ev3_cmd_filename, "a")
        except IOError:
            time.sleep(wait_period)                      # Wait for the file to be created
            continue                                     # and try again
        else:
            break
        
    ev3_file.write(message)
    
    print("-> Wrote EV3 command: {}".format(message))    # DELETE--FOR DEBUGGING
    
    ev3_file.close()

def open_connected_ev3():
    # This opens the LEGO EV3 on the bluetooth (BT) interface.  Note that the BT interface must be on and
    # paired with the LEGO EV3 for this to work.  Function returns the pointer to the serial BT interface
    # (if successful) or None if not successful
    # print('** ENTERED open_connected_ev3')
    EV3, ev3PortOpen = ev3_rpi_ctrl_pkg.openEv3()               # Port ID if successful, False otherwise
    # print('** PERFORMED ev3_rpi_ctrl_pkg.openEv3')
    # print('\n-> Ev3PortOpen {}\n'.format(ev3PortOpen))

    if ev3PortOpen is not None:
        print('\n-> Opened EV3 Brick on {}'.format(ev3PortOpen))   # Get the pointer to the open BT interface
##        print('*** EV3 type',type(EV3))
        print('\n-> EV3 Settings: name', EV3.name, EV3.get_settings())
##        print('*** Returning from open_connected_ev3()')
        return EV3, ev3PortOpen
    else:       # If no port are found
        print('\n** EV3 does not appear to be open on any /dev/rfcomm port\n')
        aiy.audio.say('EV3 does not appear to be open on any /dev/rfcomm port')
        print('*** Returning from open_connected_ev3()')
        return None, None

def process_event(assistant, event):
# Function returns a Boolean.  True means user asked the conversation to end; false otherwise

    global EV3                             # THis is the pointer to the LEGO EV3
    
    print('*** PROCESS EVENT: Point 0--Begin Process Event')
    status_ui = aiy.voicehat.get_status_ui()
    if event.type == EventType.ON_START_FINISHED:
        print('*** PROCESS EVENT: Point 1--ON_START_FINISHED')
        status_ui.status('ready')
        if sys.stdout.isatty():
            print('Say "OK, Google" then speak, or press Ctrl+C to quit...')

    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        print('*** PROCESS EVENT: Point 2--ON CONVERSATION TURN STARTED')
        status_ui.status('listening')

    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print('You said:', event.args['text'])
        print('*** PROCESS EVENT: Point 3--ON RECOGNIZING_SPEECH_FINISHED')
        text = event.args['text'].lower()
        if text == 'power off':
            print('*** PROCESS EVENT: Point 4--Local Power Off')
            assistant.stop_conversation()
            power_off_pi()
        elif text == 'reboot':
            print('*** PROCESS EVENT: Point 5--Local Reboot')
            assistant.stop_conversation()
            reboot_pi()
        elif text == 'ip address':
            print('*** PROCESS EVENT: Point 6--Local IP Address')
            assistant.stop_conversation()
            say_ip()
        elif text == 'ev3 forward' or text == 'lego forward':
            print('*** PROCESS EVENT: Point 7--Local EV3 Forward')
            assistant.stop_conversation()
            ev3Msg = "FWD"
            send_to_ev3(ev3Msg)
##            print('*** ENTERING messageGuin')
##            m = ev3_rpi_ctrl_pkg.messageGuin("EV3-CMD", 10.1,"number")  # SPG: DELETE THIS cFOR TEST ONLY
##            m = ev3_rpi_ctrl_pkg.messageGuin("EV3-CMD", ev3Msg,"text")  # SPG: UNCOMMENT THIS convert message; select EV3-CMD block to send to
##            print('*** EV3 is {}; EV3.isOpen() is {}'.format(EV3))
##            print('*** EV3.isOpen() is {}'.format(EV3.isOpen()))
##            print('*** After messageGuin()')
##            print('-> EV3 Settings', EV3.get_settings())
##            ev3_rpi_ctrl_pkg.messageSendX(EV3)   # DELETE FOR DEBUGGING
##            print('*** Enter messageSendY')
##            ev3_rpi_ctrl_pkg.messageSendY(m)     # DELETE FOR DEBUGGING
##            ev3_rpi_ctrl_pkg.messageSend(EV3, m) # send converted message # DUPLICXATE OF BELOW
##            if EV3 is not None and EV3.isOpen() is True:
##                print('\n -> Sending to EV3 msg: {} \n'.format(ev3Msg))
##                print('\n -> Encoded message to EV3: {} \n'.format(m))
##                print('*** Message is of type {}'.format(type(m)))
##                print('*** Is instance of unicode {}'.format(isinstance(m, unicode)))
##                print('*** ENTERING messageSend')
##                ev3_rpi_ctrl_pkg.messageSend(EV3, m)  # send converted message
####                time.sleep(5)                         # Wait 5 sec; MAY BE NOT NEEDED
##            else:
##                print("\n  Can't send--EV3 is not open \n")

        elif text == 'ev3 open' or text == 'open ev3' or text == 'open lego' or text == 'lego open':
            print('*** PROCESS EVENT: Point 8--Local EV3 Open')
            assistant.stop_conversation()
            EV3, ev3Port = open_connected_ev3()                 # Try to open the EV3
##            print('**** Returned from open_connected_ev3()')
            if EV3 is not None:
                aiy.audio.say('EV3 has been opened')
##                print('**** EV3 type',type(EV3))
##                print('**** EV3 name',EV3.name)
                print('-> EV3 Settings', EV3.get_settings())
            else:
                aiy.audio.say('EV3 has not been opened')
        elif text == 'exit':
            print('*** PROCESS EVENT: Point 9--LocaL eXIT')
            assistant.stop_conversation()
            exit_pi()
            return True                     # Indicate that user asked that the conversation end
  

    elif event.type == EventType.ON_END_OF_UTTERANCE:
        print('*** PROCESS EVENT: Point 10--ON_END_OF_UTTERANCE')
        status_ui.status('thinking')

    elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED
          or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
          or event.type == EventType.ON_NO_RESPONSE):
        print('*** PROCESS EVENT: Point 11')
        status_ui.status('ready')

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        print('*** PROCESS EVENT: Point 12--FATAL')
        sys.exit(1)

    print('*** PROCESS EVENT: Point 13--EXIT PROCESS EVENT')
    return False                                  # User DID NOT ask for conversation to end

def main():
    
    global EV3                                    # THis is the pointer to the LEGO EV3.  This is a declared
                                                  # as global so that during multiple calls to process_event,
                                                  # the pointer in EV3 will have a persistant value
    
    EV3 = None
    
    if platform.machine() == 'armv6l':
        print('Cannot run hotword demo on Pi Zero!')
        exit(-1)

    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    
    aiy.audio.set_tts_volume(15)                 # Set vol for local speech
    aiy.audio.set_tts_pitch(100)    

    
    with Assistant(credentials) as assistant:
        for event in assistant.start():
            exit_conv = process_event(assistant, event)
            if exit_conv:                         
                break                           # Stop this look if user requested it


if __name__ == '__main__':
    main()
