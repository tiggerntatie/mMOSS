.. _tutorial7:

mMOSS Tutorial 7: I Don't Want a Fuel Gauge on my Ship
======================================================

In the original **mMOSS** game client it was impossible to tell which
ship was yours because they all looked alike. When the fuel gauge bars
were added to the ship that belongs to you, it suddenly became obvious
(or nearly so) which one belonged to you.

But now that you've spent all that time designing the perfect custom
ship icon, wouldn't it be nice to get rid of those fuel bars and put them
someplace more sensible? Like in the corner of the screen?

Let's do it!

Z Order: Time to Get Serious
----------------------------

We mentioned this thing called "z order" a few tutorials back. Each of the
"displayable" objects (Bullet, Asteroid, Ship) have a member variable named
z. The z variable (referred to as self.z) is used to decide the order
in which things are drawn on the screen. Another way to think of that is
that z decides which things are on top. Right now asteroids and ships
have z values of 2, which places them above bullets.

Now we would like to define an on-screen fuel gage that has to be drawn on
top of everything else. So let's be explicit about the z order values of
everything so we don't get confused. Add the following lines near the top
of your **mMOSS** game file (for example, after the BULLETV and BULLETE
declarations): ::

    # Z order definitions
    ZBACKGROUND = 0
    ZBULLETS = 1
    ZSOLIDS = 2
    ZSCREENWIDGETS = 3

Now in the __init__ method of Ship change the self.z = line to read: ::

        self.z = ZSOLIDS

Do the same thing in the Asteroid __init__ method.

In the Bullet __init__ method use this line instead: ::

        self.z = ZBULLETS

A Brand New Displayable Object: HealthPanel
-------------------------------------------

After all the Bullet class methods, insert the following complete class
definition for HealthPanel: ::

    class HealthPanel(MMOSSDisplayableObject):

        """This is a representation of the ship's health that can be displayed
        on screen.
        """

        def __init__(self, *args, **kwargs):
            super(HealthPanel, self).__init__(*args, **kwargs)
            # High value z order means it will be above all other objects
            self.z = ZSCREENWIDGETS

        def displaySingleObject(self, displaytime, screen):
            """Write a weapon/fuel/shield health display in the lower left hand
            corner of the screen.

            Arguments:
            displaytime - (ignored)
            screen - Reference to pygame screen.
            Returns: List of screen rectangles affected by the image.
            """
            BARHEIGHT = 60
            x = 0
            y = self.client.screensize[1]
            ship = self.client.myshipobject
            dirtyrects = [
                pygame.draw.line(
                    screen,
                    color,
                    (x+xpos,y),
                    (x+xpos,y-BARHEIGHT*(level/maxlvl)),10) for
                color, xpos, level, maxlvl in
                    [[red, 5, ship.wlevel, ship.wmax],
                    [green, 20, ship.flevel, ship.fmax],
                    [blue, 35, ship.slevel, ship.smax]]]
            return dirtyrects


The meat of this object definition is at the end of the displaySingleObject
method. A single line of Python code, split over several text lines
draws a series of three colored vertical bars with colors, red, green and
blue, whose lengths correspond to your ship's weapon level (wlevel),
fuel level (flevel) and shield level (slevel).

In order to figure out your ship's fuel levels in the first place, the line
that reads: ::

    ship = self.client.myshipobject

retrieves a reference to your Ship object, which has the necessary
fuel level member variables (wlevel, flevel and slevel).

Clean Up the Ship displaySingleObject Method
--------------------------------------------

Now that we have code for displaying fuel levels on screen we can get rid
of the bars that are displayed on the ship itself. Just **delete** these lines
from displaySingleObject in Ship: ::

        # show fuel/health levels on OUR ship
        if self.isOurShip:
            dirtyrect.union_ip(pygame.draw.line(screen, red, (x+5,y),
                (x+5,y-20*(self.wlevel/self.wmax)),3))
            dirtyrect.union_ip(pygame.draw.line(screen, green, (x+10,y),
                (x+10,y-20*(self.flevel/self.fmax)),3))
            dirtyrect.union_ip(pygame.draw.line(screen, blue, (x+15,y),
                (x+15,y-20*(self.slevel/self.smax)),3))


Display It
----------

Now that we have defined a HealthPanel class, it's time to create an
*instance* of it so that it can be displayed. Objects that don't move around
the screen and are not sent to us from the server are known as *static
objects*. Static objects are stored in their own list in the Client. Simply
add the following lines to the end of the Client joinResponse method: ::

        self.healthobj = HealthPanel(client = self)
        self.staticobjectlist.append(self.healthobj)

The joinResponse method is called automatically when the server sends a
message that answers your request to join the server. This is the time
when the server will begin sending information to the client about
asteroids and other players, so it is appropriate to build things like
the health panel object at this time.

The first of these lines creates an *instance* of the HealthPanel class.

The second of these lines adds a reference to this HealthPanel object or
instance to a list of "static" objects. The **mMOSS** game framework
will automatically redisplay everything in the staticobjectlist at the same
time that it redisplays all of the player ships, bullets and asteroids.