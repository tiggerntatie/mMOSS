"""
mMOSS moderately Multiplayer Online Side Scroller

Classes defined:
1. Server

Copyright (c) 2011 by Eric Dennison.  All rights reserved.
"""

import random
import time
from twisted.internet import reactor
from twisted.internet import task
from serverprotocol import *
from stats import PlayerStats

POLLRATE = 0.02

__author__ = "Eric Dennison"


class Server(object):
    
    """Instantiate and run() to launch the mMOSS game server.
    """
    
    def __init__(self, port, gamedimensions, asteroiddensity):
        """Create mMOSS game server.
        
        Arguments:
        port - Internet port to listen on.
        gamedimensions - Tuple representing (W,H) dimensions of game.
        asteroiddensity - Fraction of game area consumed by asteroid material.
        """
        self.port = port
        self.clientdata = {}
        self.bulletlist = {}
        self.asteroidlist = {}
        self.playerstats = PlayerStats()
        self.idcounter = 0
        self.gamedimensions = gamedimensions
        self.spawnAsteroids(asteroiddensity)
        self.skippollcount = 0
        self.polltask = task.LoopingCall(self.serverPoll)
        self.polltask.start(POLLRATE) # call every so often
        random.seed()


    def serverPoll(self):
        """Server poll is called by Twisted to check for object expiration 
        or collisions.
        """
        if self.skippollcount:
            self.skippollcount = 0
            return
        timestamp = time.time()
        for objid,obj in self.bulletlist.items():
            # bullet lifetime expired?
            if obj.endoflife <= timestamp:
                obj.isalive = False
                for d in self.clientdata:
                    d.sendServerObjectDropEvent(obj, obj.endoflife)                
            else:
                # cache current position
                obj.cachePosition(timestamp-obj.timestamp)
        for protocol,ship in self.clientdata.items():
            # ship out of fuel
            if ship.fuelouttime <= timestamp:
                # no thrust, no shots
                ship.processCommand(timestamp,0,0,0,0)    
                # inform everyone of new thrust, fuel
                self.sendObjectToPeers(protocol,ship) 
        # get a list of ships to use
        shipitems = self.clientdata.items()
        asteroiditems = self.asteroidlist.items()
        items = shipitems+asteroiditems
        #for protocol,ship in shipitems:
        for dummy, obj in items:
            obj.cachePosition(timestamp-obj.timestamp)
        for protocol,obj in items:
            # collisions with objects (bullets, etc.)
            for bulletid,bullet in self.bulletlist.items():
                if obj.checkCollision(bullet):
                    if type(obj) is MMOSSShip:
                        if obj.processCollision(timestamp,bullet):
                            # survived, update shield levels
                            protocol.sendServerPrivateObjectStateEvent(obj) 
                        else:
                            # not survived, update shooter stats
                            self.playerstats.kill(bullet.shooter.objectname) 
                    for d in self.clientdata:   
                        # drop the bullets for everyone
                        d.sendServerObjectDropEvent(bullet, timestamp)
            # collisions with peer ships or asteroids - 
            # look at all subsequent ships in shipitems
            for protocol2,obj2 in items[items.index((protocol,obj))+1:]: 
                if obj.checkCollision(obj2):
                    # updates velocity, shields, etc. for both
                    obj.processCollision(timestamp,obj2) 
                    # update state
                    self.sendObjectToPeers(protocol,obj)           
                    self.sendObjectToPeers(protocol2,obj2)
                    
        # figure out what needs to be dropped and keep the living bullets
        self.bulletlist = dict([(objid,obj) for objid,obj in 
            self.bulletlist.items() if obj.isalive])
        dropships = [protocol for protocol,ship in self.clientdata.items() 
            if not ship.isalive]
        for protocol in dropships: self.dropClient(protocol)
        self.skippollcount = math.trunc((time.time()-timestamp)/POLLRATE)

    def sendAllObjects(self, protocol):
        """Send complete state information for all server objects to a single
        player (normally occurs on join).
        
        Arguments:
        protocol - Reference to a client connection.
        """
        objects = self.clientdata.items() + self.asteroidlist.items()
        for key,obj in objects:
            if not key is protocol:
                protocol.sendServerObjectJoinEvent(obj)
            protocol.sendServerObjectStateEvent(obj)
        for obj in self.bulletlist.values():
            protocol.sendServerObjectStateEvent(obj) # all other objects
    
    def sendNewObjectToPeers(self, protocol, obj):
        """Send complete state information for a new server object to all
        connected clients.
        
        Arguments:
        protocol - Reference to a client connection that originated the new 
        object.
        obj - Reference to the object that needs to be sent to all.
        """
        for d in self.clientdata:
            if not d is protocol:
                d.sendServerObjectJoinEvent(obj)
            
    def sendObjectToPeers(self, protocol, obj):
        """Send the object state information to all peer connections.
        
        Arguments: 
        protocol - Reference to a client connection that originated the state
        update.
        obj - Reference to the object that needs to be sent to all.
        """
        for d in self.clientdata:
            # public data
            d.sendServerObjectStateEvent(obj) 
        if type(obj) == MMOSSShip:
            # private data to owner
            protocol.sendServerPrivateObjectStateEvent(obj) 


    def dropClient(self, protocol):
        """Send a drop event to all peer connections for the ship object
        owned by this connected peer.
        
        Arguments:
        prototocol - Reference to a client connection that is dropping.
        """
        timestamp = time.time()
        if self.clientdata.has_key(protocol):
            objtodrop = self.clientdata[protocol]
            for d in self.clientdata:
                d.sendServerObjectDropEvent(objtodrop, timestamp)
            # update stats
            self.playerstats.killed(objtodrop.objectname)
            self.clientdata.pop(protocol)    # remove the client from our list
                
    def spawnAsteroids(self, density):
        """Create a random collection of asteroids.
        
        Arguments: 
        density - Fraction of the playing area that is consumed by asteroid
        material. This is normally a *small* number.
        """
        maxarea = density*self.gamedimensions[0]*self.gamedimensions[1]
        currarea = 0.0
        while currarea < maxarea:
            newid = self.getNewID()
            radius = random.randint(10,int(MAXASTEROIDRADIUS/5))
            currarea = currarea + math.pi*radius**2
            newasteroid = MMOSSAsteroid(
                objectid=newid, 
                gamedimensions=self.gamedimensions,
                rr=random.random()-0.5,
                radius=radius)
            self.spawnObjectLocation(newasteroid)   # revise location
            self.asteroidlist[newid] = newasteroid
    
    def spawnObjectLocation(self, newobj):
        """Repeatedly change object position to avoid collisions with 
        existing objects.
        
        Arguments: 
        newobj - Reference to the new object that needs to be located.
        """
        timestamp = time.time()
        # build a list of all objects
        objlist = self.clientdata.values()+self.bulletlist.values()+\
            self.asteroidlist.values()
        # trial and error: pick a spot and see if it's colliding with anything
        colliding = True
        while colliding:
            colliding = False
            newobj.X = array([random.randint(0,self.gamedimensions[0]),
                random.randint(0,self.gamedimensions[1])])
            newobj.cachePosition(timestamp-newobj.timestamp)
            for obj in objlist:
                obj.cachePosition(timestamp-obj.timestamp)
                colliding = colliding or newobj.insideCollisionDistance(obj) 

    def processClientControl(self, protocol, timestamp, thrust, ccwthrust, 
        shootv, shoote):
        """Process control message (thrust, weapon firing) and send updated
        objects to all connected peers.
        
        Arguments:
        protocol - Reference to a connection to the controlling client.
        timestamp - Server timestamp (estimated) for the control event.
        thrust - Value of commanded thrust (+ forward, - backwards).
        ccwthrust - Value of rotaitonal thrust (+ ccw).
        shootv - Speed of fired shot.
        shoote - Destructive energy of the fired shot.
        """
        # if it's not here, it must have died just before...
        if not self.clientdata.has_key(protocol): return    
        ship = self.clientdata[protocol]
        controlling, bullet = ship.processCommand(timestamp, thrust, 
            ccwthrust, shootv, shoote)
        if controlling:
            self.sendObjectToPeers(protocol, ship)
        if bullet:
            bullet.objectid = self.getNewID()
            self.bulletlist[bullet.objectid] = bullet
            self.sendObjectToPeers(protocol, bullet)
            protocol.sendServerPrivateObjectStateEvent(ship)
            
    def joinClient(self, protocol, shipname, radius, wmax, fmax, smax, image, 
            thrustimg, bulletimg):
        """Process a join request message received from a client.
        
        Arguments:
        protcol - Reference to a client connection that is joining.
        shipname - Name of the joining ship (player).
        radius - Radius of the new ship (pixels).
        wmax - Maximum weapon health level.
        fmax - Maximum fuel level.
        smax - Maximum shield level.
        image - Binary image exported from pygame.
        thrustimg - Binary imnage of thrust.
        bulletimg - Binary image of a projectile.
        Returns: Tuple with (ID of joined player, horizontal, vertical size
        of the gaming area).
        """
        newid = self.getNewID()
        newship = MMOSSShip(objectname=shipname, 
            objectid=newid, 
            gamedimensions=self.gamedimensions,
            radius=radius, 
            fmax=fmax, 
            wmax=wmax, 
            smax=smax, 
            image=image,
            thrustimg=thrustimg,
            bulletimg=bulletimg,
            x=0,
            y=0 )
        self.spawnObjectLocation(newship)   # revise location
        self.clientdata[protocol] = newship
        self.sendNewObjectToPeers(protocol,newship)
        self.sendObjectToPeers(protocol,newship)
        newship.ischanged = False
        # start keeping track of a new player
        self.playerstats.spawn(shipname)
        # client id, gamewidth, gameheight
        return newid, self.gamedimensions[0], self.gamedimensions[1]    
        
    def sendStats(self, protocol):
        """Send player stats for all players.
        
        Arguments:
        protocol - Reference to the client that requested stats.
        """
        self.playerstats.updateAllPlayTimes()
        for player in self.playerstats.getPlayers():
            protocol.sendServerPlayerStatsEvent(player)
        protocol.sendServerPlayerStatsEvent(PlayerStats.Player("",0,0,0))

    def getNewID(self):
        """Generate a unique ID for a new object.
        
        Returns: ID value.
        """
        self.idcounter = self.idcounter+1
        return self.idcounter


    def run(self):
        """Execute the Twisted ServerFActory and listen on the mMOSS TCP port.
        """
        pf = ServerFactory(self)
        reactor.listenTCP(self.port, pf)
        reactor.run()


