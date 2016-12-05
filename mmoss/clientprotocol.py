"""
mMOSS moderately Multiplayer Online Side Scroller

Classes defined:
1. ClientProtocol

Copyright (c) 2011 by Eric Dennison.  All rights reserved.
"""

from __future__ import division                                                                 
import logging
from twisted.protocols import amp
from twisted.internet import protocol

from mmoss.network import *
from mmoss.utility import *

__author__ = "Eric Dennison"

class ClientProtocol(amp.AMP):
    
    """The client protocol defines client side handlers for network messages 
    and a client side API for originating messages to the server. It is an 
    translationlayer between the network message definitions and the 
    application.
    """

    def __init__(self):
        self.objectFactory = MMOSSFactory()        

    # Handlers for connection events
    #    
    def connectionMade(self):
        """Notify the client that a connection has been made."""
        self.client = self.factory.client
        self.client.notifyConnected(self)

    def connectionLost(self, reason):
        """Notify the client that a connection has been lost."""
        self.client.notifyDisconnected()
        self.client = None

    #
    # Handlers for messages from the server
    #
    def objectStateEvent(self, objectid, objecttype, objectname, eventtime,
        x, y, vx, vy, a, r, rr):
        """Notify the client that an object state has changed.
        
        Arguments:
        objectid - Numeric ID of object.
        objecttype - Text representation of object type.
        objectname - Name of the object.
        eventtime - Server timestamp of state event.
        """
        logging.info("objectStateEvent: id: %s, type: %s, name: %s,"
            "x/y/r/vx/vy/a %f %f %f %f %f %f" % 
            (objectid, objecttype, objectname, x, y, r, vx, vy, a)) 
        obj = self.objectFactory.buildObject(objectid=objectid,
            client=self.client,
            displayable=True,
            gamedimensions=self.client.gamedimensions,
            objecttype=objecttype, 
            objectname=objectname, 
            timestamp=eventtime, 
            x=x, y=y, vx=vx, vy=vy, a=a, r=r, rr=rr)
        self.client.notifyObjectState(obj)        
        return {'result':1}

    ServerObjectStateEvent.responder(objectStateEvent)

    def objectJoinEvent(self, objectid, objecttype, objectname, radius, 
        image, imagex, imagey, thrustimg, bulletimg):
        """Notify the client that a peer/object has joined the game.
        
        Arguments:
        objectid - Numeric ID of the object.
        objecttype - Text representation of object type.
        objectname - Name of the object.
        radius - Radius of the object (pixels).
        image - Ship image as a pygame export.
        imagex - Width of ship image.
        imagey - Height of ship image.
        thrustimg - Image of thrusting (e.g. flames)
        bulletimg - Image of bullet this ship shoots.
        """
        logging.info("objectJoinEvent: id: %s, type: %s, name: %s" % 
            (objectid, objecttype, objectname))
        obj = self.objectFactory.buildObject(objectid=objectid,
            client=self.client,
            displayable=True,
            gamedimensions=self.client.gamedimensions,
            objecttype=objecttype,
            objectname=objectname,
            radius=radius,
            image=pygame.image.fromstring(image, (imagex,imagey),
                "RGBA") if objecttype==MMOSSShipType else None,
            thrustimg=thrustimg,
            bulletimg=bulletimg)
        self.client.notifyNewObject(obj)
        return {'result':1}
        
    ServerObjectJoinEvent.responder(objectJoinEvent)

    def privateObjectStateEvent(self, objectid, wlevel, flevel, slevel):
        """Notify the client of a private state update."
        
        Arguments:
        objectid - Numeric ID of the object.
        wlevel - Weapon quantity.
        flevel - Fuel level.
        slevel - Shield level.
        """
        self.client.notifyPrivateObjectState(objectid, wlevel, flevel, slevel)
        return {'result':1}

    ServerPrivateObjectStateEvent.responder(privateObjectStateEvent)

    def objectDropEvent(self, objectid, eventtime):
        """Notify client that an object has been dropped by the server.
        
        Arguments:
        objectid - Numeric ID of the object.
        eventtime - Server timestamp for the drop event.
        """
        self.client.notifyObjectDrop(objectid, eventtime)
        return {'result':1}

    ServerObjectDropEvent.responder(objectDropEvent)

    def playerStatsEvent(self, playername, playtime, killcount, killedcount):
        """Notify client of player statistics.
        
        Arguments:
        playername - Name of the player.
        playtime - Accumulated play time in seconds.
        killcount - Number of kills by player.
        killedcount - Number of times player has died.
        """
        self.client.notifyPlayerStats(playername, playtime, killcount, 
            killedcount)
        return {'result':1}

    ServerPlayerStatsEvent.responder(playerStatsEvent)

    #
    # Functions to call from the client
    #
    def callbackClientPing(self, args):
        """Handle response to the ClientPing message.
        
        Arguments:
        args - Attribute dictionary.
        """
        self.userCallbackClientPing(args['clienttime'], args['servertime'])
    
    def sendClientPing(self, timestamp, callback):
        """Generate the ClientPing message.
        
        Arguments:
        timestamp - Client timestamp for ping.
        callback - Reference to handler for ping response.
        """
        self.userCallbackClientPing = callback
        self.callRemote(ClientPing, clienttime=timestamp).addCallback(
            self.callbackClientPing)

    def sendClientControlEvent(self, shipobj):
        """Generate the ClientControlEvent message.
        
        Arguments:
        shipobj - Reference to ship that represents the user control input.
        """
        self.callRemote(ClientControlEvent, 
            timestamp=shipobj.timestamp,
            thrust=shipobj.thrust, 
            ccwthrust=shipobj.ccwthrust, 
            shootv=shipobj.shootv, 
            shoote=shipobj.shoote)
        # reset the ccwthrust
        shipobj.ccwthrust = 0.0
        # reset the shoote
        shipobj.shoote = 0.0

    def callbackClientJoinRequest(self, args):
        """Handle response to the ClientJoinRequest message.
        
        Arguments:
        args - Attribute dictionary.
        """
        self.userCallbackClientJoinRequest(args['shipid'], args['time'], 
            args['gamewidth'], args['gameheight'])

    def sendClientJoinRequest(self, ship, callback):
        """Generate the ClientJoinRequest message.
        
        Arguments:
        ship - Reference to the ship object that is joining.
        callback - Reference to a handler for the join request response.
        """
        self.userCallbackClientJoinRequest = callback
        self.callRemote(ClientJoinRequest, 
            shipname=ship.objectname, 
            radius=ship.radius, 
            wmax=ship.wmax, 
            fmax=ship.fmax, 
            smax=ship.smax,
            image=pygame.image.tostring(ship.image,"RGBA"),
            imagex=ship.image.get_width(),
            imagey=ship.image.get_height(),
            thrustimg=ship.thrustimg, 
            bulletimg=ship.bulletimg).addCallback(
                self.callbackClientJoinRequest)

    def sendClientGenericRequest(self, req):
        """Generate GenericRequest message.
        
        Arguments:
        req - Request.
        """
        self.callRemote(ClientGenericRequest, request=req)

    def sendClientGenericEvent(self, evt):
        """Generate GenericEvent message.
        
        Arguments:
        evt - Event.
        """
        self.callRemote(ClientGenericEvent, event=evt)

   
class ClientFactory(protocol.ClientFactory):
    """Twisted protocol factory for instantiating client protocol."""
    protocol = ClientProtocol

    def __init__(self, client):
        self.client = client

    def clientConnectionFailed(self, connector, reason):
        pass
    
    def clientConnectionLost(self, connector, reason):
        pass


