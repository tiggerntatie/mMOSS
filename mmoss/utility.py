"""
mMOSS moderately Multiplayer Online Side Scroller Utility Module

The utility module defines classes that encapsulate all dynamic player objects
such as player ships, asteroids, bullets, etc.

Classes defined:

#. :class:`MMOSSFactory` - MMOSSObject factory
#. :class:`MMOSSObject` - Base class for game objects.
#. :class:`MMOSSBullet` - Bullet object.
#. :class:`MMOSSSolid` - Base class for objects with mass/dimensions.
#. :class:`MMOSSShip` - Ship object.
#. :class:`MMOSSAsteroid` - Asteroid object.

Copyright (c) 2011 by Eric Dennison.  All rights reserved.
"""
from __future__ import division
import time
import math
import pygame
from numpy import array, linalg, dot
from parametric import Parametric

__author__ = "Eric Dennison"

ACCEL = 75.0
"""acceleration multiplier."""

RACCEL = 0.25
"""Rotational acceleration multiplier."""

MASS = 25.0
"""Mass multiplier."""

REFUELR = 0.5
"""Default refueling rate."""

FUELUSERATE = 0.02
"""Fuel use rate determines a fuel usage : thrust ratio."""

RFUELUSERATE = 0.002
"""Rotational fuel use rate determines a fuel usage : torque ratio."""

BULLETKEFACTOR = 0.0001
"""Bullet kinetic energy multiplier."""

SHIPKEFACTOR = 0.00001
"""Ship kinetic energy multiplier."""

BULLETENERGYFACTOR = 5.0
"""Zero velocity bullet energy multiplier."""

BULLETRANGE = 1500
"Nominal distance for a bullet to travel before expiring."""

MAXBULLETLIFE = 20
"""Seconds to live for a zero velocity bullet."""

MAXBULLETVELOCITY = 120
"""Maximum velocity for bullets."""

MINSHIPRADIUS = 5
"""Minimum radius for a player ship."""

MAXSHIPRADIUS = 50
"""Maximum radius for a player ship."""

DEFAULTRADIUS = 20
"""Default radius for all objects."""

MAXASTEROIDRADIUS = 130
"""Maximum radius of an asteroid."""

SHIPMASS = MASS
"""Customized mass multiplier for player ships."""

ASTEROIDMASS = MASS * 5
"""Customized mass multiplier for asteroids (these are heavy/dense 
rocky things"""

CR = 0.95
"""Coefficient of restitution defines degree of energy loss in collisions."""


#
# Definitions for MMOSS Objects
#

MMOSSShipType = "ship"
MMOSSBulletType = "bullet"
MMOSSAsteroidType = "asteroid"
MMOSSSolidType = "solid"

class MMOSSObject(object):
    """Generic MMOSS game entity base class.
    
    :keyword objectid: Numeric ID of object.
    :keyword objectname: Name of the object (e.g. player name).
    :keyword timestamp: Timestamp when object is created.
    :keyword x: X coordinate of position.
    :keyword y: Y coordinate of position.
    :keyword vx: X component of velocity.
    :keyword vy: Y component of velocity.
    :keyword a: Axial acceleration.
    :keyword r: Direction object is pointing (radians, zero right).
    :keyword rr: Rotational rate of object (radians per second).
    :keyword image: Reference to pygame image.
    """

    def __init__(self, *args, **kwargs):
        super(MMOSSObject, self).__init__()
        self.radius = 0
        self.ischanged = True
        self.isalive = True
        self.gamedimensions = kwargs.pop('gamedimensions', array([1, 1]))
        self.objectid = kwargs.pop('objectid', 0)
        self.objectname = kwargs.pop('objectname', '')
        self.timestamp = kwargs.pop('timestamp', time.time())
        self.X = array([kwargs.pop('x', 0.0), kwargs.pop('y', 0.0)])
        self.V = array([kwargs.pop('vx', 0.0), kwargs.pop('vy', 0.0)])
        self.a = kwargs.pop('a', 0.0)
        self.r = kwargs.pop('r', math.pi / 2.0)
        self.rr = kwargs.pop('rr', 0.0)
        self.image = kwargs.pop('image', None)
        if not self.image is None:
            self.rect = self.image.get_rect()

    def copyDynamics(self, obj):
        """Copy server-determined info into an existing object.
        """
        self.timestamp = obj.timestamp
        self.X = obj.X
        self.V = obj.V
        self.a = obj.a
        self.r = obj.r
        self.rr = obj.rr

    def directionVector(self):
        """Return a unit vector aligned with the object direction.
        """
        return array([math.cos(self.r), math.sin(self.r)])

    def forecastRates(self, deltat):
        """Calculate object velocity state corresponding to a future time.
        
        
        :param deltat: Seconds elapsed since last state update.
        :returns: Velocity vector (array)
        """
        Direction = self.directionVector()
        V = self.V
        if deltat != 0.0:
            if self.rr != 0.0:
                Temp = array([(math.sin(self.rr * deltat + self.r) - math.sin(self.r)),
                              (-math.cos(self.rr * deltat + self.r) + math.cos(self.r))])
                V = V + (self.a / self.rr) * Temp
            elif self.a != 0.0:
                V = V + self.a * deltat * Direction
        return V

    def forecastPosition(self, deltat):
        """Calculate object position corresponding to a future time.
        
        
        :param deltat: Seconds elapsed since last state update.
        :returns: Position and rotation as tuple (X vector, rotational 
        position, list of virtual positions).
        """
        # Occasionally see deltat as a complex number!!!
        savedeltat = deltat
        if not deltat.imag == 0:
            deltat = abs(deltat)
            print ("Complex deltat! old {0:f}, new {1:f}".format(savedeltat, deltat))
        if deltat != 0.0:
            X = self.X + self.V * deltat
            if self.rr != 0.0:
                Temp = array([((-math.cos(self.rr * deltat + self.r) +
                                math.cos(self.r)) / self.rr - math.sin(self.r) * deltat),
                              ((-math.sin(self.rr * deltat + self.r) +
                                math.sin(self.r)) / self.rr + math.cos(self.r) * deltat)])
                X = X + (self.a / self.rr) * Temp
            elif self.a != 0.0:
                Temp = array([0.5 * self.a * math.cos(self.r) * deltat ** 2,
                              0.5 * self.a * math.sin(self.r) * deltat ** 2])
                X = X + Temp
        else:
            X = self.X
            # true center position in game space
        ActualX = X % self.gamedimensions
        # edge positions
        VirtualXlist = [ActualX]
        try:
            if self.gamedimensions[1] - ActualX[1] < self.radius:
                VirtualXlist.append(ActualX - array([0, self.gamedimensions[1]]))
        except:
            print("Mysterious complex math bug!")
            print("dim1, actualx1, radius:", self.gamedimensions[1], ActualX[1], self.radius)
            print("deltat, X, self.X, self.rr, self.r, self.a, ActualX", deltat, X, self.X, self.rr,
                self.r, self.a, ActualX)
        if ActualX[1] < self.radius:
            VirtualXlist.append(ActualX + array([0, self.gamedimensions[1]]))
        if self.gamedimensions[0] - ActualX[0] < self.radius:
            VirtualXlist.append(ActualX - array([self.gamedimensions[0], 0]))
        if ActualX[0] < self.radius:
            VirtualXlist.append(ActualX + array([self.gamedimensions[0], 0]))
        return ActualX, self.r + self.rr * deltat, VirtualXlist

    def cachePosition(self, deltat):
        """Calculate and cache the object position. The cached position is 
        stored with the object state.
        
         
        :param deltat: Seconds elapsed since last state update.
        :returns: True
        """
        self.Xcache, self.rcache, self.Xcachelist = self.forecastPosition(deltat)
        return True

    def updateCurrentState(self, servertime):
        """Calculate the current position and velocity based on the server
        time.
        
        
        :param servertime: Current server time.
        """
        deltat = servertime - self.timestamp
        self.timestamp = servertime
        # update current position, velocity based on last command change
        V = self.forecastRates(deltat)
        self.X, self.r, self.VirtualXlist = self.forecastPosition(deltat)
        self.V = V


    def __str__(self):
        return "obj: {0:d}:{1:>s} x: {2:f}, y: {3:f}, vx: {4:f}, vy: {5:f}, r: {6:f}, rr: {7:f}"\
        .format(self.objectid, self.OBJECTTYPE, self.X[0], self.X[1],
                self.V[0], self.V[1], self.r, self.rr)


class MMOSSDisplayableObject(MMOSSObject):
    """Generic MMOSS game entity base class that can be displayed.
    """

    def __init__(self, *args, **kwargs):
        super(MMOSSDisplayableObject, self).__init__(*args, **kwargs)
        self.dirtyrects = []
        self.client = kwargs.pop('client', None)
        # z order. Lower numbers render first
        self.z = 1

    def displaySingleObject(self, displaytime, screen):
        """Write a single image to the screen. This must be overridden 
        by the inheriting class!

        
        :param displaytime: Time stamp for predicting locaiton, etc.
        :param screen: Reference to pygame screen.
        :returns: List of screen rectangles affected by the image.
        """
        return None

    def displayObject(self, displaytime, screen):
        """Update location of object and .
        
         
        :param displaytime: Time at which to display the object.
        :param screen: Reference to the pygame screen.
        :returns: List of screen rectangles affected.
        """
        self.dirtyrects = []
        self.dirtyrects.extend(
            self.displaySingleObject(displaytime, screen))
        return self.dirtyrects

    def eraseObject(self, screen):
        """Write background color to the screen rectangles that were last 
        displayed. 
        
        
        :param screen: Reference to the pygame screen.
        :returns: List of screen rectangles affected.
        """
        for dirtyrect in self.dirtyrects:
            screen.fill(self.client.background, dirtyrect)
        return self.dirtyrects


class MMOSSBullet(MMOSSObject):
    """Subclass representing a weapon projectile

    :keyword objectid: Numeric ID of object.
    :keyword objectname: Name of the object (e.g. player name).
    :keyword timestamp: Timestamp when object is created.
    :keyword x: X coordinate of position.
    :keyword y: Y coordinate of position.
    :keyword vx: X component of velocity.
    :keyword vy: Y component of velocity.
    :keyword a: Axial acceleration.
    :keyword r: Direction object is pointing (radians, zero right).
    :keyword rr: Rotational rate of object (radians per second).
    :keyword image: Reference to pygame image.
    :keyword energy: Energy (destructive) of the bullet.
    :keyword velocity: Speed of the bullet (pixels per second).
    :keyword shooter: Reference to the ship that generated it.
    :keyword azimuth: Direction of the bullet flight.
    """

    OBJECTTYPE = MMOSSBulletType

    def __init__(self, *args, **kwargs):
        super(MMOSSBullet, self).__init__(*args, **kwargs)
        self.energy = kwargs.pop('energy', 0.0)
        self.relativevelocity = kwargs.pop('velocity', 0.0)
        if self.relativevelocity > MAXBULLETVELOCITY:
            self.relativevelocity = MAXBULLETVELOCITY
        if kwargs.has_key('shooter'):
            self.shooter = kwargs.pop('shooter')
            self.shooterid = self.shooter.objectid
            deltat = self.timestamp - self.shooter.timestamp
            self.X, self.r, dummy = self.shooter.forecastPosition(deltat)
            self.V = self.shooter.forecastRates(deltat)
        if kwargs.has_key('azimuth'):
            self.r = kwargs.pop('azimuth')
        self.V = self.V + self.relativevelocity * self.directionVector()
        self.velocity = linalg.norm(self.V)
        # self.away is True when bullet has left vicinity of source
        self.away = False
        self.endoflife = self.timestamp + MAXBULLETLIFE
        if self.relativevelocity:
            self.endoflife = min(self.endoflife, self.timestamp +
                                                 BULLETRANGE / self.relativevelocity)

    def impactEnergy(self):
        """Calculate the draining effect on shields following an impact
        with another object.
        
        :returns: Destructive energy.
        """
        return BULLETENERGYFACTOR * self.energy

    def generationEnergy(self):
        """Calculate the energy required to produce this bullet shot.
        
        :returns: Generation energy.
        """
        return self.energy + BULLETKEFACTOR * self.energy * self.relativevelocity ** 2


class MMOSSSolid(MMOSSObject):
    """Sublclass representing object with mass and radius, etc.

    :keyword objectid: Numeric ID of object.
    :keyword objectname: Name of the object (e.g. player name).
    :keyword timestamp: Timestamp when object is created.
    :keyword x: X coordinate of position.
    :keyword y: Y coordinate of position.
    :keyword vx: X component of velocity.
    :keyword vy: Y component of velocity.
    :keyword a: Axial acceleration.
    :keyword r: Direction object is pointing (radians, zero right).
    :keyword rr: Rotational rate of object (radians per second).
    :keyword image: Reference to pygame image.
    :keyword radius: Radius of the object (pixels).
    """

    def __init__(self, *args, **kwargs):
        super(MMOSSSolid, self).__init__(*args, **kwargs)
        self.radius = kwargs.pop('radius', DEFAULTRADIUS)
        self.mass = MASS * self.radius ** 2 / 100
        # list of entities currently kissing
        self.collidingwith = []

    def insideCollisionDistance(self, otherobj):
        """Compare the cached position of the object against the cached
        position of another object.
        
         
        :param otherobj: Reference to the other object.
        :returns: True if within contact range, False otherwise.
        """
        distlist = [(X, linalg.norm(self.Xcache - X))
                    for X in otherobj.Xcachelist]
        otherobj.Xclosest, distance = min(distlist, key=lambda X:X[1])
        if type(otherobj) is MMOSSBullet:
            return distance < self.radius
        elif isinstance(otherobj, MMOSSSolid):
            return distance < (self.radius + otherobj.radius)
        else:
            return False

    def checkCollision(self, otherobj):
        """Compare the cached position of the object against the cached 
        position of another object. Determine the outcome of the potential
        collision.
         
        :param otherobj: Reference to the other object.
        
        :returns: True if collision has occurred, False otherwise.
        """
        hit = self.insideCollisionDistance(otherobj)
        if type(otherobj) is MMOSSBullet:
            if otherobj.away and otherobj.isalive:
                return hit
            elif not hit and (otherobj.shooterid ==
                              self.objectid and otherobj.isalive):
                otherobj.away = True
        elif isinstance(otherobj, MMOSSSolid):
            if hit:
                if not otherobj in self.collidingwith:
                    self.collidingwith.append(otherobj)
                else:
                # already processed collision with this solid
                    hit = False
            elif otherobj in self.collidingwith:
                # not colliding any more
                self.collidingwith.remove(otherobj)
            return hit
        return False

    def processSolidCollision(self, servertime, othersolid):
        """Compute new state for object and another solid object following
        an elastic collision. Function will update the current state of both
        objects as a side effect.
        
        
        :param servertime: Current time on the server.
        :param othersolid: Reference to the other colliding object.
        """
        self.updateCurrentState(servertime)
        othersolid.updateCurrentState(servertime)
        m1 = self.mass
        m2 = othersolid.mass
        P1 = Parametric(self.X, self.V)
        P2 = Parametric(othersolid.Xclosest, othersolid.V)
        # compute collision based on the instant the objects would have touched
        collisiontimes = P1.timeatdistance(P2, self.radius + othersolid.radius)
        if len(collisiontimes) > 0:
            tcollision = min(collisiontimes)
            self.updateCurrentState(servertime + tcollision)
            otheroldX = othersolid.X
            othersolid.updateCurrentState(servertime + tcollision)
            # tweak the Xclosest vector to match
            othersolid.Xclosest = othersolid.Xclosest + othersolid.X - otheroldX
            R = othersolid.Xclosest - self.X

            # construct unit vector normal to plane of collision
            R = R / linalg.norm(R)
            # scalar component of velocity normal to plane
            u1 = dot(self.V, R)
            # scalar component, other solid
            u2 = dot(othersolid.V, R)
            # new velocities after semi-elastic collision
            # see http://en.wikipedia.org/wiki/Inelastic_collision
            A = m1 * u1 + m2 * u2
            B = m1 + m2
            v1 = (CR * m2 * (u2 - u1) + A) / B
            v2 = (CR * m1 * (u1 - u2) + A) / B
            #v1 = (u1*(m1-m2)+2*m2*u2)/(m1+m2)
            #v2 = (u2*(m2-m1)+2*m1*u1)/(m1+m2)
            self.V = self.V + R * (v1 - u1)
            othersolid.V = othersolid.V + R * (v2 - u2)
            self.processCollisionDeltaV(v1 - u1)
            othersolid.processCollisionDeltaV(v2 - u2)

    def processCollisionDeltaV(self, deltav):
        """Process consequences of a collision deltav. This function should
        be overridden by child classes.
        
        
        :param deltav: Change in velocity for this object.
        """
        return


class MMOSSAsteroid(MMOSSSolid):
    """Subclass of MMOSSSolid representing an asteroid object.

    :keyword objectid: Numeric ID of object.
    :keyword objectname: Name of the object (e.g. player name).
    :keyword timestamp: Timestamp when object is created.
    :keyword x: X coordinate of position.
    :keyword y: Y coordinate of position.
    :keyword vx: X component of velocity.
    :keyword vy: Y component of velocity.
    :keyword a: Axial acceleration.
    :keyword r: Direction object is pointing (radians, zero right).
    :keyword rr: Rotational rate of object (radians per second).
    :keyword image: Reference to pygame image.
    :keyword radius: Radius of the object (pixels).
    """

    OBJECTTYPE = MMOSSAsteroidType

    def __init__(self, *args, **kwargs):
        super(MMOSSAsteroid, self).__init__(*args, **kwargs)
        if self.radius > MAXASTEROIDRADIUS:
            self.radius = MAXASTEROIDRADIUS
        self.mass = ASTEROIDMASS * self.radius ** 2 / 100

    def processCollision(self, servertime, otherobj):
        """Assuming a collision has occurred, assess the damage.
        
        
        :param servertime: Collision time on the server.
        :param otherobj: Reference to the other colliding object.
        :returns: True if still alive, False otherwise.
        """
        if type(otherobj) is MMOSSBullet:
            otherobj.isalive = False    # assumes other object is a bullet!
        elif isinstance(otherobj, MMOSSSolid):
            self.processSolidCollision(servertime, otherobj)
        return True


class MMOSSShip(MMOSSSolid):
    """Subclass of MMOSSSolid representing a player ship.

    :keyword objectid: Numeric ID of object.
    :keyword objectname: Name of the object (e.g. player name).
    :keyword timestamp: Timestamp when object is created.
    :keyword x: X coordinate of position.
    :keyword y: Y coordinate of position.
    :keyword vx: X component of velocity.
    :keyword vy: Y component of velocity.
    :keyword a: Axial acceleration.
    :keyword r: Direction object is pointing (radians, zero right).
    :keyword rr: Rotational rate of object (radians per second).
    :keyword image: Reference to pygame image.
    :keyword radius: Radius of the object (pixels).
    :keyword wmax: Weapon max energy (0-100).
    :keyword fmax: Fuel max energy (0-100).
    :keyword smax: Shield max energy (0-100).
    :keyword thrustimg: Reference to pygame thrust image.
    :keyword bulletimg: Reference to pygame bullet image.
    """

    OBJECTTYPE = MMOSSShipType

    def __init__(self, *args, **kwargs):
        super(MMOSSShip, self).__init__(*args, **kwargs)
        wmax = kwargs.pop('wmax', 30)    # weapon max energy
        fmax = kwargs.pop('fmax', 40)    # fuel max energy
        smax = kwargs.pop('smax', 30)    # shield max energy
        self.thrustimg = kwargs.pop('thrustimg', '')
        self.bulletimg = kwargs.pop('bulletimg', '')
        if self.radius > MAXSHIPRADIUS:
            self.radius = MAXSHIPRADIUS
        if self.radius < MINSHIPRADIUS:
            self.radius = MINSHIPRADIUS
            # enforce total of wmax,fmax,smax is 100
        if wmax == 0 and fmax == 0 and smax == 0:
            wmax = fmax = smax = 33
        factor = 100.0 / (wmax + fmax + smax)
        wmax, fmax, smax = [maxlvl * factor for maxlvl in [wmax, fmax, smax]]
        if wmax > 100:
            wmax = 100
        if wmax + fmax > 100:
            fmax = 100 - wmax
        smax = 100 - wmax - fmax
        self.wmax, self.fmax, self.smax = wmax, fmax, smax
        self.mass = SHIPMASS * self.radius ** 2 / 100
        self.defaultmass = SHIPMASS * DEFAULTRADIUS ** 2 / 100
        self.energycapacity = self.mass # capacity is proportional to mass
        self.defaultenergycapacity = self.defaultmass
        # adjust categories for total capacity
        self.energyfactor = self.energycapacity / self.defaultenergycapacity
        self.wmax = self.wmax * self.energyfactor
        self.fmax = self.fmax * self.energyfactor
        self.smax = self.smax * self.energyfactor
        self.wlevel = self.wmax
        self.flevel = self.fmax
        self.slevel = self.smax
        self.wrate = REFUELR    # refuel rate
        self.frate = REFUELR    # refuel rate
        self.srate = REFUELR    # refuel rate
        self.wuserate = 0.0
        self.fuserate = 0.0
        self.suserate = 0.0
        self.thrust = 0.0
        self.ccwthrust = 0.0
        self.shootv = 0.0
        self.shoote = 0.0
        self.fuelouttime = 1E3000

    def forecastFuel(self, deltat):
        """Calculate fuel levels for some time after last update.
        
        :param deltat: Seconds since last object update.
        
        :returns: List of levels: (weapon, fuel, shield)
        """
        levels = [min(level - (userate - rate) * deltat, maxval) for
                  level, userate, rate, maxval in
                  [(self.wlevel, self.wuserate, self.wrate, self.wmax),
                   (self.flevel, self.fuserate, self.frate, self.fmax),
                   (self.slevel, self.suserate, self.srate, self.smax)]]
        levels = [0 if level < 0 else level for level in levels]
        return levels

    def forecastFuelOut(self):
        """Calculate time remaining at current use rate before fuel is 
        exhausted.
        
        :returns: Seconds until fuel is out.
        """
        if self.fuserate <= self.frate:
            return 1E3000  # signifies never runs out
        return self.flevel / (self.fuserate - self.frate)

    def processCollision(self, servertime, otherobj):
        """Assuming a collision has occurred, assess the damage.
                
        :param servertime: Collision time on the server.
        :param otherobj: Reference to the other colliding object.
        :returns: True if still alive, False otherwise.
        """
        if type(otherobj) is MMOSSBullet:
            self.slevel = self.slevel - otherobj.impactEnergy()
            otherobj.isalive = False    # assumes other object is a bullet!
        elif isinstance(otherobj, MMOSSSolid):
            self.processSolidCollision(servertime, otherobj)
        self.isalive = self.slevel >= 0.0
        return self.isalive

    def processCollisionDeltaV(self, deltav):
        """Calculate damage to ship shield due to change in velocity
        following a collision.
        
         
        :param deltav: Change in velocity for this object.
        """
        self.slevel = self.slevel - SHIPKEFACTOR * self.mass * deltav ** 2
        self.isalive = self.slevel >= 0.0

    def updateFuel(self, wlevel, flevel, slevel):
        """Update the ship fuel levels.
        
        
        :param wlevel: New weapon level.
        :param flevel: New fuel level.
        :param slevel: New shield level.
        """
        self.wlevel = wlevel
        self.flevel = flevel
        self.slevel = slevel

    def updateCurrentState(self, servertime):
        """Update ship position, velocity and fuel levels based on current
        server time and current use rates.
        
         
        :param servertime: Current time on the server.
        """
        deltat = servertime - self.timestamp
        super(MMOSSShip, self).updateCurrentState(servertime)
        self.wlevel, self.flevel, self.slevel = self.forecastFuel(deltat)


    def processCommand(self, servertime, thrust, ccwthrust, shootv, shoote):
        """Calculate new acceleration and fuel use rates based on thrust and
        weapon use commands.
        
        :param servertime: Current server time.
        :param thrust: Value of commanded thrust (+ for forward, - for reverse).
        :param ccwthrust: Value of commanded rotational thrust (+ for ccw).
        :param shootv: Value of commanded weapon shot velocity.
        :param shoote: Value of commanded weapon shot destructive energy.
        
        :returns: Tuple of (True if ship is maneuvering, True if a shot has 
                  been fired).
        """
        # do nothing if no changes
        shotfired = False
        maneuvering = True
        if thrust == self.thrust and ccwthrust == 0.0:
            maneuvering = False
        self.updateCurrentState(servertime)
        self.thrust = thrust
        self.ccwthrust = ccwthrust
        self.a = ACCEL * thrust / self.mass
        self.fuserate = abs(thrust) * FUELUSERATE
        # rotational impulse (including fuel use)
        raccel = RACCEL * ccwthrust / self.mass
        fueluse = RFUELUSERATE * abs(ccwthrust)
        if fueluse <= self.flevel:
            self.rr = self.rr + raccel
            # avoid fp errors near zero
            if abs(self.rr) < 1.0E-10:
                self.rr = 0.0
            self.flevel = self.flevel - fueluse
        self.fuelouttime = self.timestamp + self.forecastFuelOut()
        # process the shot
        if not shoote == 0.0:
            bullet = MMOSSBullet(gamedimensions=self.gamedimensions,
                                 shooter=self, energy=shoote, velocity=shootv)
            shooteused = bullet.generationEnergy()
            if shooteused <= self.wlevel:
                self.wlevel = self.wlevel - shooteused
                shotfired = bullet
                self.shoote = shoote
                self.shootv = shootv
            else:
                self.shoote = self.shootv = 0.0
        return maneuvering, shotfired


class MMOSSFactory(object):
    """The factory class is responsible for instantiating game objects
    of various types, in response to messages from the server.
    """

    def __init__(self):
        """Build list of object classes that ARE and ARE NOT displayable.
        """
        self.notdisplayableclasses = self.getUsableSubclasses(
            MMOSSObject, False)
        self.displayableclasses = self.getUsableSubclasses(
            MMOSSObject, True)

    def getUsableSubclasses(self, parent, displayable):
        """Recursive function walks the inheritance tree looking for 
        classes with OBJECTTYPE defined and displayable (or not).
        
        
        :param parent: Base class to walk from.
        :param displayable: Return displayable classes only, if True.
        :returns: List of classes that meet the criteria
        """
        usable = []
        for cls in parent.__subclasses__():
            if "OBJECTTYPE" not in dir(cls) or (
            displayable and ("displayObject" not in dir(cls))):
                usable.extend(self.getUsableSubclasses(cls, displayable))
            else:
                usable.append(cls)
        return usable


    def buildObject(self, *args, **kwargs):
        """Instantiate an object that is descended from the MMOSSObject class.
                
        :keyword objecttype: Text identification of class. One of ["ship","bullet",
                             "asteroid","solid"]
        :keyword displayable: True if must be able to be drawn (client side)
        
        MMOSSObject 
        
        :keyword objectid: Numeric ID of object.
        :keyword objectname: Name of the object (e.g. player name).
        :keyword timestamp: Timestamp when object is created.
        :keyword x: X coordinate of position.
        :keyword y: Y coordinate of position.
        :keyword vx: X component of velocity.
        :keyword vy: Y component of velocity.
        :keyword a: Axial acceleration.
        :keyword r: Direction object is pointing (radians, zero right).
        :keyword rr: Rotational rate of object (radians per second).
        :keyword image: Reference to pygame image.
        
        MMOSSBullet 
        
        :keyword energy: Energy (destructive) of the bullet.
        :keyword velocity: Speed of the bullet (pixels per second).
        :keyword shooter: Reference to the ship that generated it.
        :keyword azimuth: Direction of the bullet flight.
        
        MMOSSSolid 
        
        :keyword radius: Radius of the object (pixels).
        
        MMOSSAsteroid 
        
        MMOSSShip 
        
        :keyword wmax: Weapon max energy (0-100).
        :keyword fmax: Fuel max energy (0-100).
        :keyword smax: Shield max energy (0-100).
        :keyword thrustimg: Reference to pygame thrust image.
        :keyword bulletimg: Reference to pygame bullet image.
        
        :returns: the instantiated object.
        """
        objecttype = kwargs.pop('objecttype', '')
        displayable = kwargs.pop('displayable', False)
        if displayable:
            classes = self.displayableclasses
        else:
            classes = self.notdisplayableclasses
        for cls in classes:
            if cls.OBJECTTYPE == objecttype:
                return cls(*args, **kwargs)


        
