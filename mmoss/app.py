#! /usr/bin/python

"""mMOSS moderately Multiplayer Online Side Scroller

Game client/server application class. It Handles command line options and 
launches the server or chosen client.

Classes defined:
1. MMOSSApp

Copyright (c) 2011 by Eric Dennison.  All rights reserved.
"""

import os
import argparse
import logging
import platform
from mmoss.server import Server
from mmoss.network import *


__author__ = "Eric Dennison"

SERVER_LOG_FILENAME = 'log/mmossserver.log'
CLIENT_LOG_FILENAME = 'log/mmossclient.log'

POLL_RATE = 0.02

class MMOSSApp(object):
    
    """Encapsulate mMOSS application.
    
    The mMOSS application class serves two roles:
    1. Argument parsing
    2. Decision to launch server or client code.
    """
    
    def __init__(self, clientclass):
        """Initialize application. Define command line arguments."""
        self.client = clientclass
        parser = argparse.ArgumentParser(
                            description='moderately Multiplayer '
                                        'Online Space Shooter.')
        parser.add_argument('--width','-W', metavar='WIDTH', type=int, 
                            default=800,
                            help='client window or server field width')
        parser.add_argument('--height','-H', metavar='HEIGHT', type=int, 
                            default=550,
                            help='client window or server field height')
        parser.add_argument('--port','-p', metavar='PORT', type=int, 
                            default=MMOSS_PROTOCOL, help='Internet port')
        parser.add_argument('--refresh-rate','-r', metavar='RATE', type=float,
                            default=1.0/POLL_RATE, 
                            help='screen refresh rate (Hz)')
        parser.add_argument('--player-name','-n', metavar='PLAYERNAME', 
                            type=str,
                            default=platform.node(), help='player name')
        parser.add_argument('--server-address','-a', metavar='SERVERIPADDR', 
                            type=str,
                            default='127.0.0.1', 
                            help='IP address of the game server')
        parser.add_argument('--server','-s', action='store_true',  
                            help='run mMOSS as a server')
        parser.add_argument('--log','-l', action='store_true', 
                            help='log mMOSS events')
        self.parser = parser


    def parseArguments(self):
        """Parse command line arguments and return arguments."""
        self.args = self.parser.parse_args()
        return self.args


    def run(self):
        """Execute the application according to passed arguments."""
        if self.args.server:
            if self.args.log:
                logging.basicConfig(filename=SERVER_LOG_FILENAME,
                    level=logging.DEBUG)
            s = Server(self.args.port, 
                (self.args.width,self.args.height), 0.005)
            s.run()
        else:
            if self.args.log:
                logging.basicConfig(filename=CLIENT_LOG_FILENAME,
                    level=logging.DEBUG)
            s = self.client(self.args, self.args.server_address, 
                 self.args.port, 1.0/self.args.refresh_rate, 
                 self.args.player_name, (self.args.width,self.args.height))
            s.run()

