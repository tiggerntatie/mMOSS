"""
mMOSS moderately Multiplayer Online Side Scroller

The client module defines a base class for implementing a mMOSS client.

Classes defined:
1. MMOSSClient

Copyright (c) 2011 by Eric Dennison.  All rights reserved.
"""

import sys
import os.path
import time
import logging
import pygame
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.internet import task
from network import REQUEST_FULLUPDATE
from utility import MMOSSShip, MMOSSBullet, MMOSSAsteroid
from controller import Controller
from stats import PlayerStats
from clientprotocol import ClientFactory

__author__ = "Eric Dennison"


class MMOSSClient(object):

    """The MMOSSClient class encapsulates basic functionality required
    for interacting with the twisted AMP protocol and pygame user interface.
    Users are expected to subclass MMOSSClient to customize and extend 
    default behavior.
    
    Create a client that connects to the mMOSS server, interacts with 
    the human player and displays game state.
    
    :param arguments: argparse arguments object
    :param address: IP address (in text form e.g. "127.0.0.1")
    :param port: Internet port number
    :param refreshrate: Screen refresh rate (seconds per cycle)
    :param playername: Name of the player
    :param screensize: Tuple that specifies requested screen area (W,H)
    """
    
    
    def __init__(self, arguments, address, port, refreshrate, playername, 
        screensize):
        pygame.init() 
        self.controller = Controller([])
        self.lastpoll = time.time()
        self.timedelta = 0.0
        self.rate = refreshrate
        self.playername = playername
        self.screensize = screensize
        self.factory = ClientFactory(self)
        self.myshipobject = None
        self.gamedimensions = (1,1)
        self.shipimage = None
        self.arguments = arguments
        self.id = 0
        self.playerstats = PlayerStats()
        self.hasjoined = False
        self.hasjoinresponse = False
        self.objectlist = {}
        self.staticobjectlist = []
        reactor.connectTCP(address, port, self.factory)
        return

    def serverTime(self):
        """Compute best guess of the server time.time() at this moment.
        
        :rtype: tuple of current system time, server system time.
        """
        thetime = time.time()
        return time.time()+self.timedelta, thetime

    def notifyConnected(self, protocol):
        """When the client is connected to the server, this initializes
        state related to this connection and launches periodic tasks via
        twisted.
        
        :param protocol: identifier of the connection
        """
        self.protocol = protocol    # use protocol to send messages, etc
        self.polltask = task.LoopingCall(self.clientPoll)
        self.polltask.start(self.rate) # call every so often
        # create a task to periodically ping the server
        self.pingtask = task.LoopingCall(self.pingPoll)
        self.pingtask.start(1) # once per second
        
    def notifyDisconnected(self):
        """When the client is disconnected from the server, this stops
        the periodic tasks.
        """
        self.polltask.stop()
        self.pingtask.stop()

    def notifyObjectState(self, obj):
        """Update internal representations for objects when new object
        state is received from the server.
        
        :param obj: Instantiated temporary object.
        :type obj: MMOSSObject
        """
        if obj.objectid == self.id:
            # this is US, so just update parameters
            self.myshipobject.copyDynamics(obj)
        elif self.objectlist.has_key(obj.objectid):
            # update an existing object
            self.objectlist[obj.objectid].copyDynamics(obj)
        elif not isinstance(obj, MMOSSShip):
            # this is a new foreign object (but not a ship)
            self.objectlist[obj.objectid] = obj
        
    def notifyNewObject(self, obj):
        """Create an internal representation of an object that has just 
        been created by a different client.
        
        :param obj: Instantiated object.
        :type obj: MMOSSObject

        """
        if not obj.objectid == self.id:
            self.objectlist[obj.objectid] = obj

    def notifyPrivateObjectState(self, objectid, wlevel, flevel, slevel):
        """Update internal representation for an object that is owned by
        this client (i.e. private). This informs the client of changes to its
        health or energy levels as a result of interactions with other objects.
        
        :param objectid: Numeric ID of the object that is being updated.
        :type objectid: int
        :param wlevel: Weapon energy level.
        :param flevel: Fuel energy level.
        :param slevel: Shield energy level.
        """
        if objectid == self.id:
            self.myshipobject.updateFuel(wlevel, flevel, slevel)

    def notifyObjectDrop(self, objectid, eventtime):
        """Remove internal representations of objects that have been removed
        from the server.
        
        :param objectid: Numeric ID of the object that is being dropped.
        :type objectid: int
        :param eventtime: Server time stamp for the drop event
        """
        deadobj = self.objectlist.pop(objectid,None)
        if deadobj:
            self.deadobjectlist.append(deadobj)
        if objectid == self.myshipobject.objectid:
            self.hasjoined = False  # this will force us to rejoin!            

    def notifyPlayerStats(self, playername, playtime, killcount, killedcount):
        """Update internal record of peer player statistics.
        
        :param playername: Text identification of a player name.
        :param playtime: Seconds that the player has been online.
        :param killcount: The number of times the player has killed another player.
        :param killedcount: The number of times the player has died/respawned.
        """
        if not playername=="":
            self.playerstats.createPlayer(playername, playtime, killcount, 
                killedcount)
        else:
            self.notifyPlayerStatsComplete()
            
    def notifyPlayerStatsComplete(self):
        """Process display or reporting of all player stats to the user. This
        method is called when all of the player stats have been received.
        """
        pass
        
    def joinResponse(self, myid, thetime, gamewidth, gameheight):
        """Initialize internal state in response to succesfully connecting
        to the server. Send a request to the server to report full game state
        to the client.
        
        :param myid: Numeric ID of the client's ship.
        :param thetime: Server time stamp for the join event.
        :param gamewidth: Width of the game field (not necessarily viewport).
        :param gameheight: Height of the game field (not necessarily viewport).
        """
        if myid:
            self.hasjoinresponse = True
            self.id = myid
            self.timedelta = thetime-time.time()
            self.gamedimensions = (gamewidth,gameheight)
            # center the screen on the game (ulx, uly, width, height)
            self.screenrect = ((gamewidth-self.screensize[0])/2,
                (gameheight+self.screensize[1])/2, 
                self.screensize[0], self.screensize[1])
            self.myshipobject.gamedimensions = self.gamedimensions
            self.objectlist = {}    # clean out our object list
            self.staticobjectlist = []
            self.deadobjectlist = []
            self.myshipobject.objectid = myid
            self.objectlist[myid] = self.myshipobject
            self.protocol.sendClientGenericRequest(REQUEST_FULLUPDATE)
            logging.info("joinResponse:my id: %d , server time: %f, deltat: %f"
                % (myid, thetime, self.timedelta))

    def pingResponse(self, originalclienttime, servertime):
        """Process a period ping response from the server. Modifies a running
        average of the timedelta attribute.
        
        :param originalclienttime: Client timestamp when ping request was sent.
        :param servertime: Server timestamp when ping reply was sent.
        """
        TC = 30
        now = time.time()
        # weight current delta, but add in current delta + estimated latency
        self.timedelta = (TC*self.timedelta+(servertime-now + 
            (now-originalclienttime)/2.0))/(TC+1)

    def sendJoinRequest(self):
        """Create a new ship object and send a join request to the server.
        """
        self.hasjoined = True
        self.hasjoinresponse = False

    def gameToScreenCoordinates(self,  X):
        """Convert cartesian game coordinates to pygame screen coordinates.
        
        :rtype: tuple of (x,y) coordinates.
        """
        x,y = X
        gx,gy = self.gamedimensions[0], self.gamedimensions[1]
        sx,sy = self.screenrect[0], self.screenrect[1]
        return (x-sx)%gx, (sy-y)%gy

    def handleControls(self):
        """Keep track of the keys that have been pressed and issue an 
        appropriate control message to the server.
        """
        pass

    def eraseScreen(self):
        """Periodic call to erase screen objects.
        """
        if self.hasjoined and self.hasjoinresponse:
            self.changedrects = []
            for obj in self.deadobjectlist:
                self.changedrects.extend(obj.eraseObject(self.screen))
            self.deadobjectlist = []
            for obj in self.objectlist.values()+self.staticobjectlist:
                self.changedrects.extend(obj.eraseObject(self.screen))

    def writeScreen(self):
        """Periodic call to write screen objects in correct z order.
        """
        if self.hasjoined and self.hasjoinresponse:
            for obj in sorted(self.objectlist.values()+self.staticobjectlist, 
                key=lambda obj: obj.z):
                self.changedrects.extend(obj.displayObject(self.servertime, self.screen))
            pygame.display.update(self.changedrects)
            #pygame.display.flip()

    def clientPoll(self):
        """Perform periodic processing on the client: poll the user input.
        This function should be overridden to perform screen updates and user
        input processing.
        """
        self.servertime, self.clienttime = self.serverTime()
        self.lastpoll = self.clienttime
        self.controller.pollControls()
        if not self.hasjoined:
            self.sendJoinRequest()
        elif self.hasjoinresponse:
            self.eraseScreen()
            self.writeScreen()
            self.handleControls()

    def pingPoll(self):
        """Perform periodic processing on the client to gauge the network
        latency in client/server communications.
        """
        self.protocol.sendClientPing(time.time(), self.pingResponse)
        
    def run(self):
        """Run the twisted reactor loop."""
        reactor.run()

    def stop(self):
        """Stop the twisted reactor loop."""
        reactor.stop()

