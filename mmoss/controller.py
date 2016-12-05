"""
mMOSS moderately Multiplayer Online Side Scroller

Classes defined:
1. Controller - Encapsulate player control inputs.
2. Key - Abstract keyboard key.

Copyright (c) 2011 by Eric Dennison.  All rights reserved.
"""

from __future__ import division
import time
import pygame

__author__ = "Eric Dennison"


# definitions for keys
A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z =   \
    [chr(x) for x in range(ord('a'),ord('z')+1)]
TAB = "\t"
SPACE = " "
UP,DOWN,RIGHT,LEFT = ['up','down','right','left']
_1 = "1"



class Controller(object):
    
    """Class to encapsulate polling and interpretation of user keyboard and
    mouse control inputs.
    """

    def __init__(self,keylist):
        """Initialize instance.
        
        Arguments:
        keylist - list of keys to monitor (e.g. [A,B,C])
        """
        self.keystomonitor = [Key(k) for k in keylist]
        self.activekeys = {}
        self.pollcount = 0

    def pollControls(self):
        """Poll the pygame keyboard and mouse and update the state of keys.
        """
        currtime = time.time()
        self.pollcount = self.pollcount+1
        for k in self.activekeys:
            key = self.activekeys[k]
            key.wasdown = key.down
            key.down = False
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        for k in self.keystomonitor:
            if keys[k.pygamekey]:
                k.lastpoll = self.pollcount
                if not (k.wasdown or k.helddown):
                    k.helddown = False
                if k.wasdown:
                    k.helddown = True
                k.down = True
                if not self.activekeys.has_key(k.key):    # new key
                    self.activekeys[k.key] = k
                    k.downpoll = self.pollcount
            else:
                k.helddown = False

    def clearKey(self,keystr):
        """Remove key from activekeys list.
        
        Arguments:
        keystr - Text identifier of key to remove.
        """
        self.activekeys.pop(keystr)

    def key(self,keystr):
        """Locate and return reference to a key.
        
        Arguments: 
        keystr - Text identifier of key to return.
        Returns a Key reference or None if none is found.
        """
        if self.activekeys.has_key(keystr):
            return self.activekeys[keystr]
        else:
            return None


class Key(object):
    
    """Abstraction of the pygame keys. 
    
    Important attributes of an instance are:
    down - True when the key is currently depressed.
    helddown - True when the key has been held down for more than one
    consecutive poll cycle.
    """
    
    keymap = {  A:pygame.K_a,
                B:pygame.K_b,
                C:pygame.K_c,
                D:pygame.K_d,
                E:pygame.K_e,
                F:pygame.K_f,
                G:pygame.K_g,
                H:pygame.K_h,
                I:pygame.K_i,
                J:pygame.K_j,
                K:pygame.K_k,
                L:pygame.K_l,
                M:pygame.K_m,
                N:pygame.K_n,
                O:pygame.K_o,
                P:pygame.K_p,
                Q:pygame.K_q,
                R:pygame.K_r,
                S:pygame.K_s,
                T:pygame.K_t,
                U:pygame.K_u,
                V:pygame.K_v,
                W:pygame.K_w,
                X:pygame.K_x,
                Y:pygame.K_y,
                Z:pygame.K_z,
                UP:pygame.K_UP,
                DOWN:pygame.K_DOWN,
                RIGHT:pygame.K_RIGHT,
                LEFT:pygame.K_LEFT,
                SPACE:pygame.K_SPACE,
                TAB:pygame.K_TAB,
                _1:pygame.K_1
              }

    def __init__(self, key):
        """Initialize state.
        """
        self.key = key
        self.pygamekey = self.keymap[key]
        self.lastpoll = 0   # most recent poll count
        self.downpoll = 0   # poll count when depressed
        self.down =     False # currently down
        self.helddown = False # down for more than one poll cycle
        self.wasdown = False

