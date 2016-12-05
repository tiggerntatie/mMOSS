#!/usr/bin/python
"""
mMOSS moderately Multiplayer Online Side Scroller

mMOSS client - 
Tutorial 1. Change background color and asteroid color.
Tutorial 2. Show rotating ship image.
Tutorial 3. Customize ship image.
Tutorial 4. Panning screen window, 
Tutorial 4A: F to follow, ON/OFF

Copyright (c) 2011 by Eric Dennison.  All rights reserved.
"""
from __future__ import division
import sys
import time
import math
import pygame
from numpy import array
from mmoss.client import MMOSSClient
from mmoss.network import REQUEST_STATSUPDATE, EVENT_QUIT
from mmoss.utility import MMOSSShip, MMOSSBullet, MMOSSAsteroid
from mmoss.controller import Controller
from mmoss.utility import MMOSSDisplayableObject, MMOSSFactory
from mmoss.controller import A,S,D,Q,W,SPACE,TAB,LEFT,RIGHT,UP,DOWN,F
from mmoss.app import MMOSSApp

__author__ = "Eric Dennison"

# Define some color tuples (Red, Green, Blue). Color values are between
# 0 and 255. 0 represents no color. 255 reprsents full color.
white = 255, 255, 255
red = 255, 0, 0
blue = 0, 0, 255
green = 0, 255, 0
black = 0, 0, 0

# Repeat held keys every REPEAT_RATE seconds
REPEAT_RATE = 0.2 

# Default thrust level for rotating.
ROTATETHRUST = 100.0

# Default forward thrust level.
THRUST = 100.0

# Default bullet velocity.
BULLETV = 50.0

# Default bullet energy.
BULLETE = 3.0                                       

#
# Game Objects
#

class Ship(MMOSSShip, MMOSSDisplayableObject):
    
    """Subclass representing an player ship.
    """

    def __init__(self, *args, **kwargs):
        super(Ship,self).__init__(*args, **kwargs)
        self.isOurShip = kwargs.pop('isourship',False)
        # display above bullets
        self.z = 2
        # cache rotated images
        self.imagecache = {}

    def displaySingleObject(self, displaytime, screen):
        """Write a single ship to the screen, with special handling if 
        the ship belongs to the client.

        Arguments:
        displaytime - Time at which to display.
        screen - Reference to pygame screen.
        Returns: List of screen rectangles affected by the image.
        """
        X,r,Xlist = self.forecastPosition(displaytime-self.timestamp)
        x,y = map(int,self.client.gameToScreenCoordinates(X))
        rdegrees = round(math.degrees(r)) % 360
        if self.imagecache.has_key(rdegrees):
            rotatedimage = self.imagecache[rdegrees]
        else:
            rotatedimage = pygame.transform.rotate(self.image, rdegrees)
            self.imagecache[rdegrees] = rotatedimage
        shiprect = self.rect.move(
            x-rotatedimage.get_width()/2, y-rotatedimage.get_height()/2)
        dirtyrect = screen.blit(rotatedimage, shiprect)
        # show fuel/health levels on OUR ship
        if self.isOurShip:
            dirtyrect.union_ip(pygame.draw.line(screen, red, (x+5,y),
                (x+5,y-20*(self.wlevel/self.wmax)),3))
            dirtyrect.union_ip(pygame.draw.line(screen, green, (x+10,y),
                (x+10,y-20*(self.flevel/self.fmax)),3))
            dirtyrect.union_ip(pygame.draw.line(screen, blue, (x+15,y),
                (x+15,y-20*(self.slevel/self.smax)),3))
        return [dirtyrect]


class Asteroid(MMOSSAsteroid, MMOSSDisplayableObject):
    
    """Subclass representing an asteroid.
    """

    def __init__(self, *args, **kwargs):
        super(Asteroid,self).__init__(*args, **kwargs)
        # display above bullets
        self.z = 2

    def displaySingleObject(self, displaytime, screen):
        """Write a single asteroid to the screen.

        Arguments:
        displaytime - Time at which to display.
        screen - Reference to pygame screen.
        Returns: List of screen rectangles affected by the image.
        """
        X,r,Xlist = self.forecastPosition(displaytime-self.timestamp)
        x,y = map(int,self.client.gameToScreenCoordinates(X))
        dirtyrect = pygame.draw.line(screen, white, (x, y), 
            (x+self.radius*math.cos(r),y-self.radius*math.sin(r)))
        dirtyrect.union_ip(
            pygame.draw.circle(screen, white, (x, y), int(self.radius), 1))
        return [dirtyrect]


class Bullet(MMOSSBullet, MMOSSDisplayableObject):
    
    """Subclass representing a weapon projectile
    """

    def __init__(self, *args, **kwargs):
        super(Bullet,self).__init__(*args, **kwargs)

    def displaySingleObject(self, displaytime, screen):
        """Write a single bullet to the screen.

        Arguments:
        displaytime - Time at which to display.
        screen - Reference to pygame screen.
        Returns: List of screen rectangles affected by the image.
        """
        X,r,Xlist = self.forecastPosition(displaytime-self.timestamp)
        x,y = map(int,self.client.gameToScreenCoordinates(X))
        dirtyrect = pygame.draw.line(screen, red, (x-3,y-3),(x+3,y+3))
        dirtyrect.union_ip(pygame.draw.line(screen, red, (x+3,y-3),(x-3,y+3)))
        return [dirtyrect]


class Client(MMOSSClient):

    """The Client class overrides MMOSSClient and implements the user look
    and feel of the mMOSS game.
    """

    def __init__(self, arguments, address, port, refreshrate, playername, 
        screensize):
        """Create a client that connects to the mMOSS server, interacts with 
        the human player and displays game state.
        
        Arguments:
        arguments - argparse arguments object
        address - IP address (in text form e.g. "127.0.0.1")
        port - Internet port number
        refreshrate - Screen refresh rate (seconds per cycle)
        playername - Name of the player
        screensize - Tuple that specifies requested screen area (W,H)
        """
        super(Client,self).__init__(arguments, address, port, refreshrate, 
            playername, screensize)
        self.controller = Controller([
            A,S,D,W,Q,SPACE,TAB,LEFT,RIGHT,UP,DOWN,F])
        self.rotateheld = False
        self.lastrotate = 0.0
        self.shipimage = pygame.image.load("mmossfiles/mmossship.png")
        self.shiprect = self.shipimage.get_rect()
        self.myshipobject = None
        self.outoffuel = False
        self.background = black
        self.following = True

    #
    # Handlers for event notifications from the server
    #

    def notifyConnected(self,protocol):
        """Perform any processing required when a connection is created with
        the game server. Call the base class handler.
        
        Arguments:
        protocol - Reference to the server connection.
        """
        MMOSSClient.notifyConnected(self,protocol) 

    def joinResponse(self, myid, thetime, gamewidth, gameheight):
        """After requesting that the server admit the client, the server
        will send a response message, which is handled in this method.
        
        Arguments: 
        myid - The numeric ID of MY ship.
        thetime - The current server time.
        gamewidth - The width of the game field (pixels).
        gameheight - The height of the game field (pixels).
        """
        super(Client,self).joinResponse(myid, thetime, gamewidth, gameheight)
        size = width, height = self.gamedimensions
        self.myshipobject.gamedimensions = size
        self.screen = pygame.display.set_mode(self.screensize)
        self.screen.fill(self.background)
        pygame.display.flip() 

    def notifyPlayerStatsComplete(self):
        """Do something to let the player know what the current server/player
        statistics are.
        """
        for player in self.playerstats.getPlayers():
            print player

    # 
    # Check for user input
    #

    def handleControls(self):
        """Keep track of the keys that have been pressed and issue an 
        appropriate control message to the server.
        """
        super(Client, self).handleControls()
        if self.myshipobject:
            if self.myshipobject.flevel == 0.0:
                self.outoffuel = True
            thrust = self.checkThrustControl()
            ccwthrust = self.checkRotationalThrustControl()
            bullete = self.checkFireControl()
            controlling, shooting = self.myshipobject.processCommand(
                self.servertime, thrust, ccwthrust, BULLETV, bullete)
            if controlling or shooting:
                self.protocol.sendClientControlEvent(self.myshipobject)
        self.checkStatsControl()
        self.checkQuitControl()
        self.checkPanControls()

    def checkPanControls(self):
        """Handle arrow keys, used to pan the display window over the game
        area."""
        left, right, up, down, follow = map(
            self.controller.key, (LEFT, RIGHT, UP, DOWN, F))
        mvx = mvy = 0
        if left and left.down: mvx=-5
        if right and right.down: mvx=5
        if up and up.down: mvy=5
        if down and down.down: mvy=-5
        if follow and follow.down and not follow.helddown:
            self.following = not self.following
        if self.following:
            X,r,Xlist = self.myshipobject.forecastPosition(
                self.servertime-self.myshipobject.timestamp)
            self.screenrect = (X[0]-self.screensize[0]/2,
                X[1]+self.screensize[1]/2,self.screenrect[2],self.screenrect[3])   
        else:
            self.screenrect = (self.screenrect[0]+mvx,
                self.screenrect[1]+mvy, self.screenrect[2], self.screenrect[3])

    def checkThrustControl(self):
        """Handle forward (W) and reverse (S) thrust keys.
        
        Returns: Thrust strength (force).
        """
        fwd = self.controller.key(W)
        rev = self.controller.key(S)
        if fwd and not fwd.down and self.outoffuel:
            self.outoffuel = False
        if fwd and fwd.down and not self.outoffuel:
            thrust = THRUST
        elif rev and rev.down:
            thrust = -THRUST/5
        else:
            thrust = 0.0
        return thrust

    def checkRotationalThrustControl(self):
        """Handle left (A) and right (D) rotational thrust keys.
        
        Returns: Rotational thrust strength (torque). CCW is +.
        """
        ccwthrust = 0.0
        helddown = False
        left = self.controller.key(A)
        if left:
            if left.down:
                ccwthrust = ROTATETHRUST
            if left.helddown:
                helddown = True
        right = self.controller.key(D)
        if right:
            if right.down:
                ccwthrust = ccwthrust-ROTATETHRUST
            if right.helddown:
                helddown = True
        if helddown and self.servertime < self.lastrotate + REPEAT_RATE:
            ccwthrust = 0.0
        else:
            self.lastrotate = self.servertime
        return ccwthrust

    def checkFireControl(self):
        """Handle the fire (SPACE) key.
        
        Returns: Energy of the bullet (0.0 if none fired).
        """
        fire = self.controller.key(SPACE)
        if fire and fire.down and not fire.helddown:
            bullete = BULLETE
        else:
            bullete = 0.0
        return bullete
        
    def checkStatsControl(self):
        """Handle the "show stats" (TAB) key.
        """
        tab = self.controller.key(TAB) 
        if tab and tab.down and not tab.helddown:
            self.protocol.sendClientGenericRequest(REQUEST_STATSUPDATE)
            
    def checkQuitControl(self):
        """Handle the quit (Q) key.
        """
        if self.controller.key(Q):
            self.protocol.sendClientGenericEvent(EVENT_QUIT)
            self.stop()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()


    #
    # Periodic processing
    #

    def sendJoinRequest(self):
        """Create a new ship object and send a join request to the server.
        """
        super(Client,self).sendJoinRequest()
        self.myshipobject = Ship(
            client=self,
            radius=30,
            wmax=40, 
            fmax=30,
            smax=30, 
            image=self.shipimage,
            objectname=self.playername,
            isourship=True)
        self.protocol.sendClientJoinRequest(self.myshipobject, self.joinResponse)

    def eraseScreen(self):
        """Periodic call to erase screen objects.
        """
        super(Client,self).eraseScreen()

    def writeScreen(self):
        """Periodic call to write screen objects.
        """
        super(Client,self).writeScreen()

    def clientPoll(self):
        """Periodic processing to monitor player control/keyboard activity
        and update ship/asteroid/bullet positions on the screen.
        """
        super(Client,self).clientPoll() 

#
# Create and run the application here
#
app = MMOSSApp(Client)
# add an argument - this parameter will be available as self.arguments.ship_image 
# in the client code.
app.parser.add_argument('--ship-image','-i', metavar='SHIPIMG', type=str,
    default='rocket', help='saucer or rocket')
args = app.parseArguments()
app.run()

