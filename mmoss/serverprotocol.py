"""
mMOSS moderately Multiplayer Online Side Scroller

Classes defined:
1. ServerProtocol

Copyright (c) 2011 by Eric Dennison.  All rights reserved.
"""

from __future__ import division
import time
import logging
from twisted.protocols import amp
from twisted.internet import protocol
from mmoss.network import *
from mmoss.utility import *
from mmoss.server import *

__author__ = "Eric Dennison"

class ServerProtocol(amp.AMP):
    
    """The server protocol defines server side handlers for network messages 
    and a server side API for originating messages to the client. It is a 
    translationlayer between the network message definitions and the 
    application.
    """

    # Handlers for connection events
    #    
    def connectionMade(self):
        """Notify the server that a connection has been made."""
        logging.info("connectionMade: transport %s" % 
            (self.transport.client.__str__()))
        self.server = self.factory.server

    def connectionLost(self, data):
        """Notify the server that a connecton has been lost."""
        self.server.dropClient(self)
        self.server = None

    #
    # Handlers for messages from the client
    #
    def ping(self, clienttime):
        """Notify the server that a ping has been received.
        
        Arguments:
        clienttime - Timestamp of ping at the client.
        """
        return {'clienttime':clienttime, 'servertime':time.time()}

    ClientPing.responder(ping)

    def joinRequest(self, shipname, radius, wmax, fmax, smax, image, imagex, 
        imagey, thrustimg, bulletimg):
        """Notify the server that a client is joining the game.
        
        Arguments:
        shipname - The name of the ship/player that is joining.
        radius - Radius of the ship (in pixels).
        wmax - Maximum weapon health level (0-100).
        fmax - Maximum fuel level (0-100).
        smax - Maximum shield level (0-100).
        image - Bitmap image of the ship icon (pygame export).
        imagex - Width of the ship image.
        imagey - Height of the ship image.
        thrustimg - Bitmap image of the ship thrust (e.g. flame).
        bulletimg - Bitmap image of the bullets the ship fires.
        """
        newid, gamewidth, gameheight = self.server.joinClient(self, 
            shipname, 
            abs(radius),
            abs(wmax),
            abs(fmax),
            abs(smax),
            pygame.image.fromstring(image, (imagex,imagey),"RGBA"), 
            thrustimg, 
            bulletimg)
        return {'shipid':newid, 'time':time.time(), 'gamewidth':gamewidth, 
            'gameheight':gameheight}

    ClientJoinRequest.responder(joinRequest)

    # ClientControlEvent
    def controlCommand(self, timestamp, thrust, ccwthrust, shootv, shoote):
        """Notify server of a player control command.

        Message attributes:
        timestamp - Timestamp of control event.
        thrust - Forward/reverse thrust force.
        ccwthrust - Counter-clockwise thrust impulse.
        shootv - Velocity of a fired bullet.
        shoote - Energy of a fired bullet.
        """
        self.server.processClientControl(self,
            timestamp,
            thrust,
            ccwthrust,
            abs(shootv),
            abs(shoote))
        return {'result':1}

    ClientControlEvent.responder(controlCommand)

    def genericRequest(self, request):
        """Notify server of a generic client request.
        
        Arguments:
        request - String code for a request.
        """
        if request == REQUEST_FULLUPDATE:
            self.server.sendAllObjects(self)
        elif request == REQUEST_STATSUPDATE:
            self.server.sendStats(self)
        return {'result':1}
        
    ClientGenericRequest.responder(genericRequest)

    def genericEvent(self, event):
        """Notify server of a generic client event.
        
        Arguments:
        request - String code for an event.
        """
        if event == EVENT_QUIT:
            self.server.dropClient(self)
        return {'result':1}
        
    ClientGenericEvent.responder(genericEvent)

    #
    # Functions to call from the server
    #

    def sendServerObjectStateEvent(self, obj):
        """Generate the server object state event.
        
        Arguments: 
        obj - Reference to an object.
        """
        logging.info("sendServerObjectStateEvent: %s" %(obj))
        self.callRemote(ServerObjectStateEvent,
            objectid=obj.objectid,
            objecttype=obj.OBJECTTYPE,
            objectname=obj.objectname,
            eventtime=obj.timestamp,
            x=obj.X[0],
            y=obj.X[1],
            vx=obj.V[0],
            vy=obj.V[1],
            a=obj.a,
            r=obj.r,
            rr=obj.rr)
        
    def sendServerObjectJoinEvent(self, obj):
        """Generate the server object joined event.
        
        Arguments: 
        obj - Reference to an object.
        """
        logging.info("sendServerObjectJoinEvent: %s" % (obj))
        if type(obj) is MMOSSShip:
            self.callRemote(ServerObjectJoinEvent,
                objectid=obj.objectid,
                objecttype=obj.OBJECTTYPE,
                objectname=obj.objectname,
                radius=obj.radius,
                image=pygame.image.tostring(obj.image,"RGBA"),
                imagex=obj.image.get_width(),
                imagey=obj.image.get_height(),
                thrustimg="",
                bulletimg="")
        elif type(obj) is MMOSSAsteroid:
            self.callRemote(ServerObjectJoinEvent,
                objectid=obj.objectid,
                objecttype=obj.OBJECTTYPE,
                objectname="",
                radius=obj.radius,
                image="",
                imagex=0,
                imagey=0,
                thrustimg="",
                bulletimg="")

    def sendServerPrivateObjectStateEvent(self, obj):
        """Generate a server private object state event.
        
        Arguments:
        obj - Reference to an object.
        """
        logging.info("sendServerPrivateObjectStateEvent: private id: "
            "%d wlevel: %f flevel: %f slevel: %f" % (obj.objectid, 
                obj.wlevel, obj.flevel, obj.slevel))
        self.callRemote(ServerPrivateObjectStateEvent,
            objectid=obj.objectid,
            wlevel=obj.wlevel,
            flevel=obj.flevel,
            slevel=obj.slevel)


    def sendServerObjectDropEvent(self, obj, time):
        """Generate a server object drop event.
        
        Arguments:
        obj - Reference to an object.
        time - Timestamp of the drop event.
        """
        logging.info("sendServerObjectDropEvent: %s" % (obj))
        self.callRemote(ServerObjectDropEvent,
            objectid=obj.objectid,
            eventtime=time)
        
    def sendServerPlayerStatsEvent(self, player):
        """Generate a player statistics event for a single player.
        
        Arguments:
        player - Reference to a single player statistics.
        """
        logging.info("sendServerStatsEvent: %s %f %d %s" % 
            (player.name, player.playtime, player.killcount, 
                player.killedcount))
        self.callRemote(ServerPlayerStatsEvent, 
            playername=player.name,
            playtime=player.playtime,
            killcount=player.killcount,
            killedcount=player.killedcount)

class ServerFactory(protocol.ServerFactory):
    """Twisted protocol factory for instantiating server protocol."""
    protocol = ServerProtocol

    def __init__(self, server):
        self.server = server


