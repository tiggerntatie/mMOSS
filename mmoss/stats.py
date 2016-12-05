"""
mMOSS moderately Multiplayer Online Side Scroller

Classes defined:

PlayerStats - Track player statistics server-side

Copyright (c) 2011 by Eric Dennison.  All rights reserved.
"""

from __future__ import division
import time

__author__ = "Eric Dennison"



class PlayerStats(object):
    
    """Track the statistics for all players joining since the server started.
    """

    class Player(object):

        """Track the statistics for a single player since the server started.
        """
        
        def __init__(self, name, playtime, killcount, killedcount):
            """
            Instantiate a Player statistics tracker.
            
            Arguments:
            name - Name of the player.
            playtime - Accumulated play time in seconds.
            killcount - Number of kills the player has made.
            killedcount - Number of deaths the player has experienced.
            """
            self.name = name
            self.playtime = playtime
            self.killcount = killcount
            self.killedcount = killedcount
            self.starttime = 0
            
        def __str__(self):
            return "player %s: time %f kills: %d, deaths: %d" % (self.name, 
                self.playtime, self.killcount, self.killedcount)

    def __init__(self):
        self.players = {}
        
    def createPlayer(self, name, playtime=0.0, killcount=0, killedcount=0):
        """Start tracking a new player's statistics"""
        self.players[name] = PlayerStats.Player(name,playtime,killcount,
            killedcount)
    
    def getPlayers(self):
        """Return a list of PlayerStats.Player objects being tracked."""
        return self.players.values()
        
    def spawn(self,name):
        """Start tracking a new or respawned player.
        
        Arguments:
        name - Name of the player to track.
        """
        if not self.players.has_key(name):
            self.createPlayer(name)
        self.players[name].starttime=time.time()

    def updateAllPlayTimes(self):
        """Update play time for all tracked players."""
        for player in self.players.values():
            self.updatePlayTime(player.name)
    
    def updatePlayTime(self,name):
        """Update play time for a single player.
        
        Arguments:
        name - Name of the player to update.
        """
        now = time.time()
        player = self.players[name]
        player.playtime = player.playtime + now - player.starttime
        player.starttime = now
                
    def killed(self,name):
        """Increment the killed count for a player.
        
        Arguments:
        name - Name of the player to kill.
        """
        player=self.players[name]
        player.killedcount = player.killedcount + 1
        self.updatePlayTime(name)
    
    def kill(self,name):
        """Increment the kill count for a player.
        
        Argumens:
        name - Name of the player that killed another.
        """
        player=self.players[name]
        player.killcount = player.killcount + 1
        self.updatePlayTime(name)
        

