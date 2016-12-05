"""
mMOSS moderately Multiplayer Online Side Scroller

The Parametric class encapsulates a simple linear parametric equation. 

Copyright (c) 2011 by Eric Dennison.  All rights reserved.
"""
from __future__ import division
from numpy import array, dot, sqrt, roots
from numpy.linalg import norm


__author__ = "Eric Dennison"

class Parametric(object):
    
    """A simple class that encapsulates a linear parametric equation."""

    def __init__(self, X, V):
        """Create a parametric equation object.
        
        Arguments:
        X - Numpy array representing position at t=0
        V - Numpy array representing velocity vector
        """
        self.X = X
        self.V = V

    def position(self, t):
        """Compute an updated position vector at some time.
        
        Arguments:
        t - Seconds
        Returns a position vector (Numpy array).
        """
        return self.X + self.V*t
        
    def _distancecoefficients(self, otherobj):
        """Compute coefficients of a function for d**2.
        
        Arguments:
        otherobj - another Parametric object
        Returns (A,B,C) of d**2 = A*t**2 + B*t + C.
        """
        dx = otherobj.X-self.X
        dv = otherobj.V-self.V
        return (norm(dv)**2, 2*dot(dx,dv), norm(dx)**2)
    
    def distance(self, otherobj, t):
        """Compute distance at some time.
        
        Arguments:
        otherobj - another Parametric object
        t - time to compute distance
        Returns distance
        """
        A,B,C = self._distancecoefficients(otherobj)
        return sqrt(A*t**2 + B*t + C)
    
    def timeatdistance(self, otherobj, d):
        """Times at which objects are at a given distance.
        
        Arguments:
        otherobj - another Parametric object
        d - distance between objects
        Returns list of times when objects are at given distance
        """

        A,B,C = self._distancecoefficients(otherobj)
        return roots((A,B,C-d**2))
    
    def positionatdistance(self, otherobj, d, earliest=True):
        """Positions of objects at a given distance.
        
        Arguments:
        otherobj - another Parametric object
        d - distance between objects
        earliest - True to return earliest position at distance
        Returns two position vectors corresponding to self and otherobj
        """
        tlist = self.timeatdistance(otherobj, d)
        t = min(tlist) if earliest else max(tlist)
        return self.position(t), otherobj.position(t)
        

