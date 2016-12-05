.. _tutorial6:

mMOSS Tutorial 6: Follow that Ship!
===================================

In the last tutorial: :ref:`tutorial5`, you modified **mMOSS** to give
you a panning window into a (potentially) much larger playing area.
Unfortunately, the responsibility for keeping track of where *your*
ship is and panning the window to follow it is entirely yours. What a pain
in the neck!

Wouldn't it be nice if we could have **mMOSS** *follow* the ship as it
moves around the game area?

Map Another Key
---------------

We are going to create a "following" mode so it would make sense to map
the "F" key for that purpose. Go in and add F to the controller import
line at the beginning of your file and add F again to the Client __init__
code where the controller is created. Refer to the previous tutorial
if you would like a reminder on where to find those.

Are we Following?
-----------------

Your **mMOSS** program will have to keep track of whether it is following
your ship or not. It will remember this state by using a member variable
in the Client object. Add the following line at the end of the Client
__init__ method: ::

        self.following = True

This will guarantee that when you start the game your own ship will be
at the center of the screen and will stay there until you decide to
stop following it.

Modify checkPanControls
-----------------------

We'll need to make some adjustments in checkPanControls, the method that
we added in the last tutorial. Change the first code line in checkPanControls
to read: ::

        left, right, up, down, follow = map(
            self.controller.key, (LEFT, RIGHT, UP, DOWN, F))

All we did here is add the F key to the list of keys that we want to look
at in this method and assigned it to a variable called "follow".

Next, Insert the following lines *just before* the last line in
checkPanControls: ::

        if follow and follow.down and not follow.helddown:
            self.following = not self.following
        if self.following:
            X,r,Xlist = self.myshipobject.forecastPosition(
                self.servertime-self.myshipobject.timestamp)
            self.screenrect = (X[0]-self.screensize[0]/2,
                X[1]+self.screensize[1]/2,self.screenrect[2],self.screenrect[3])
        else:


.. note::

    The code we inserted ends with an *else:* statement, which means that
    the existing last line of the method (where you manually control the
    panning) will only be executed if we are
    **not**
    in following mode. Don't forget to indent that original last line of
    code (Python will yell at you if you don't).

The first bit of this new code simply checks to see if the user has pressed
the "follow" key (which is F). If she did, then just change the state of the
self.following variable to be the opposite ("not") of what it used to be. If
it was "True" then it will become "False". If it was "False" then it will
become "True". This sort of behavior is often referred to as "toggling".

Next, if the self.following variable is True the code finds out what your
ship's current position is (the 2D vector X) and then moves the screen
rectangle (self.screenrect) so that it is directly over the ship.