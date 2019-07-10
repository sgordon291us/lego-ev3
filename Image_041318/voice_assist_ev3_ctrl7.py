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

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import logging
import platform
import subprocess
import sys
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
    
    status_ui = aiy.voicehat.get_status_ui()
    if event.type == EventType.ON_START_FINISHED:
        status_ui.status('ready')
        if sys.stdout.isatty():
            print('Say "OK, Google" then speak, or press Ctrl+C to quit...')

    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        status_ui.status('listening')

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
                ev3_rpi_ctrl_pkg.messageSend(EV3, m)  # send converted message
            else:
                print("\n  Can't send--EV3 is not open \n")
        elif text == 'ev3 open' or text == 'open ev3' or text == 'open lego' or text == 'lego open':
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
            assistant.stop_conversation()
            exit_pi()
            return True                     # Indicate that user asked that the conversation end
  

    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')

    elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED
          or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
          or event.type == EventType.ON_NO_RESPONSE):
        status_ui.status('ready')

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)

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
