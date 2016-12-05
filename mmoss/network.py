"""
mMOSS moderately Multiplayer Online Side Scroller

Network message class definitions.

Protocol commands are named [Client/Server]Fucntion[Request/Event]. 
Client/Server indicates which end of the connection ORIGINATES the message. 

Copyright (c) 2011 by Eric Dennison.  All rights reserved.
"""
from __future__ import division
from twisted.protocols import amp

MMOSS_PROTOCOL = 12171

REQUEST_FULLUPDATE = "r_fu"
REQUEST_STATSUPDATE = "r_su"
EVENT_QUIT       = "e_qu"


class ClientPing(amp.Command):
    """Client originated ping message for gauging latency.
    
    Message attributes:
    clienttime - timestamp at client when ping generated.
    Response attributes:
    clienttime - timestamp at client when ping generated.
    servertime - timestamp at server when ping response generated.
    """
    arguments = [('clienttime', amp.Float())]
    response = [('clienttime', amp.Float()),
                ('servertime', amp.Float())]

class ClientControlEvent(amp.Command):
    """Client user control event.
    
    Message attributes:
    timestamp - Timestamp of control event.
    thrust - Forward/reverse thrust force.
    ccwthrust - Counter-clockwise thrust impulse.
    shootv - Velocity of a fired bullet.
    shoote - Energy of a fired bullet.    
    """
    arguments = [('timestamp', amp.Float()),
                 ('thrust', amp.Float()),
                 ('ccwthrust',amp.Float()),
                 ('shootv', amp.Float()),
                 ('shoote', amp.Float())]

class ClientJoinRequest(amp.Command):
    """Client join/respawn request.
    
    Message attributes:
    shipname - User/player name.
    radius - Radius of the ship in pixels.
    wmax - Weapon relative maximum level (0-100).
    fmax - Fuel relative maximum level (0-100).
    smax - Shield relative maximum level (0-100).
    image - Bitmap of the ship icon (pygame format).
    imagex - Width of image.
    imagey - Height of image.
    thrustimg - Bitmap of the ship thrusting image.
    bulletimg - Bitmap of the ship's bullet image.
    """
    arguments = [('shipname',amp.String()),
                    ('radius',amp.Integer()),
                    ('wmax',amp.Integer()),
                    ('fmax',amp.Integer()),
                    ('smax',amp.Integer()),
                    ('image',amp.String()),
                    ('imagex',amp.Integer()),
                    ('imagey',amp.Integer()),
                    ('thrustimg',amp.String()),
                    ('bulletimg',amp.String())]
    response = [('shipid',amp.Integer()),('time',amp.Float()),
        ('gamewidth',amp.Integer()),('gameheight',amp.Integer())]

class ClientGenericRequest(amp.Command):
    """Generic client request.
    
    Message attributes:
    request - String code for a request.
    Response attributes:
    result - 1 for success.
    """
    arguments = [('request',amp.String())]
    response = [('result', amp.Integer())]

class ClientGenericEvent(amp.Command):
    """Generic client event.
    
    Message attributes:
    event - String code for an event.
    Response attributes:
    result - 1 for success.
    """
    arguments = [('event',amp.String())]
    response = [('result',amp.Integer())]

class ServerObjectStateEvent(amp.Command):
    """Server object state change event.
    
    Message attributes:
    objectid - Numeric ID of object.
    objecttype - Text representation of object type.
    objectname - Name of object.
    eventtime - Timestamp of object event.
    x - X coordinate of object position.
    y - Y coordinate of object position.
    vx - X component of object velocity.
    vy - Y component of object velocity.
    a - Axial acceleration of object.
    r - Rotational position of object in radians (0 points up).
    rr - Rotational rate of object in radians/second.
    Response attributes:
    result - 1 for success.
    """
    arguments = [('objectid', amp.Integer()),  
                 ('objecttype', amp.String()), 
                 ('objectname', amp.String()), 
                 ('eventtime', amp.Float()),   
                 ('x', amp.Float()),           
                 ('y', amp.Float()),           
                 ('vx', amp.Float()),
                 ('vy', amp.Float()),
                 ('a', amp.Float()), 
                 ('r', amp.Float()), 
                 ('rr', amp.Float())]
    response = [('result', amp.Integer())]
    
class ServerObjectJoinEvent(amp.Command):
    """Server object join/spawn event.
    
    Message attributes:
    objectid - Numeric ID of object.
    objecttype - Text representation of object type.
    objectname - Name of object.
    radius - Radius of the ship in pixels.
    image - Bitmap of the ship icon (pygame format).
    imagex - Width of image.
    imagey - Height of image.
    thrustimg - Bitmap of the ship thrusting image.
    bulletimg - Bitmap of the ship's bullet image.
    Response attributes:
    result - 1 for success.
    """    
    arguments = [('objectid', amp.Integer()),  
                 ('objecttype', amp.String()), 
                 ('objectname', amp.String()),
                 ('radius', amp.Integer()),
                 ('image', amp.String()),  
                 ('imagex', amp.Integer()),
                 ('imagey', amp.Integer()),
                 ('thrustimg', amp.String()),
                 ('bulletimg', amp.String())]
    response = [('result', amp.Integer())]
                 
class ServerPrivateObjectStateEvent(amp.Command):
    """Server private object state event.
    
    Message attributes:
    objectid - Numeric ID of the object.
    wlevel - Weapon health level.
    flevel - Fuel health level.
    slevel - Shield health level.
    Response attributes:
    result - 1 for success.
    """
    arguments = [('objectid',amp.Integer()), 
                 ('wlevel',amp.Float()),     
                 ('flevel',amp.Float()),     
                 ('slevel',amp.Float())]     
    response = [('result', amp.Integer())]

class ServerObjectDropEvent(amp.Command):
    """Server object drop event. An object has died/exploded/quit, etc.
    
    Message attributes:
    objectid - Numeric ID of the object.
    eventtime - Timestamp of drop.
    Response attributes:
    result - 1 for success.
    """
    arguments = [('objectid', amp.Integer()),
                 ('eventtime', amp.Float())] 
    response = [('result', amp.Integer())]   

class ServerPlayerStatsEvent(amp.Command): 
    """Server player stats event.
    
    Message attributes:
    playername - Name of player - empty string when done.
    playtime - Cumulative seconds of play time.
    killcount - Total number of kills since connected.
    killedcount - Total number of deaths since connected.
    Response attributes:
    result - 1 for success.
    """
    arguments = [('playername', amp.String()),
                 ('playtime', amp.Float()),   
                 ('killcount', amp.Integer()),
                 ('killedcount',amp.Integer())
                ]
    response = [('result', amp.Integer())]    

