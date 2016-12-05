.. _tutorial2:

mMOSS Tutorial 2: Rotate the Ship Icon
======================================

If you finished :ref:`tutorial1` then you have learned how to work with
the **mMOSS** sources, making changes and testing those changes. In that
tutorial you made some minor modifications to the source code, changing
the screen background color and the asteroid colors. In this tutorial,
we take this process a little further and customize the ship icon,
giving it the power to rotate.

Modifying the Ship Object
-------------------------

Your code already loads an image file that represents your ship.
Unfortunately, the image doesn't rotate! This modification will
use the ship image that you've already loaded and rotate it to match
the position of the ship.

First off, rotating the ship icon takes a fair amount of processing power.
By default, your client program redraws the screen 50 times per second.
If your ship is rotating all the time, the client will have to calculate
a rotated version of your ship icon 50 times per second!

Not only that, since you will have custom icons for all the *other*
players in the game, your client program will have to rotate *their*
icons too. Ouch!

To avoid doing all these image rotations, we will also add some code to
save the rotated images and reuse them as necessary.

Look in your source code for a line like this: ::

    class Ship(MMOSSShip, MMOSSDisplayableObject):

This is a special line that creates a **class** definition in the program.
A class is a sort of *super* function that can represent both data or
information and the code for manipulating it. This class is used to
represent and display both your and other players ship objects. Since our
goal is to change the way ships are displayed in the game then we should
be making changes in this class.

Below the class declaration (above) there are two class *methods*: ::

    def __init__(self, *args, **kwargs):

and ::

    def displaySingleObject(self, displaytime, screen):

The __init__ method is called once when each ship object is created. This
occurs
in the game when you join the server (for both your own ship and all the
other players' ships) or when other players join the server (for their
ships).

Modify the __init__ Method
++++++++++++++++++++++++++

Look at the __init__ method. You should see some lines like this: ::

        super(Ship,self).__init__(*args, **kwargs)
        self.isOurShip = kwargs.pop('isourship',False)
        # display above bullets
        self.z = 2

The Ship class is actually a child of a much more complicated class called
MMOSSShip (defined in a different file). The first line here, calling
"super" will call the
__init__ method of the parent class, so it can do any initialization.

The next line checks to see if **this** Ship object is, in fact, supposed
to represent **our** ship. It will set a *member variable* called isOurShip
so that it is True if it is our ship, or False if it is not.

The last line (following the comment) sets the "z order" of the object.
Objects are displayed on the screen in a certain order, so that background
objects are drawn first, followed by foreground objects. The higher the
z order value, the later the object will be displayed.

In order to keep track of the rotated icons for this ship object, add
the following lines at the end of the __init__ method: ::

        # cache rotated images
        self.imagecache = {}

This code creates a member variable of the Ship object called **imagecache**.
The image cache is set equal to "{}", which means that it is an empty
Python dictionary. A dictionary is a data storage device that lets you
store an unlimited number of things and find them again based on a name
that you choose. More on that later...


Modify the displaySingleObject Method
+++++++++++++++++++++++++++++++++++++

Next we'll look at the displaySingleObject method (below the __init__
method).

There are two major parts to this method: ::

        X,r,Xlist = self.forecastPosition(displaytime-self.timestamp)
        x,y = map(int,self.client.gameToScreenCoordinates(X))
        shiprect = self.rect.move(x-self.rect[2]/2, y-self.rect[3]/2)
        dirtyrect = screen.blit(self.image, shiprect)
        dirtyrect.union_ip(pygame.draw.line(screen, red, (x,y),
            (x+20*math.cos(r),y-20*math.sin(r))))

The first line in this section figures out *where* the ship is in the game.
The method called :meth:`forecastPosition` figures out where the ship is
(a vector variable: X), what direction it's pointed (r), and a list of
virtual locations if the ship is wrapping around the edge of the playing
area (Xlist).

The second line converts the ship's position to screen coordinates (x,y).

The third and fourth lines position the ship image rectangle (self.rect)
on the screen and copies the image to it (screen.blit of self.image).

The dirtyrect variable keeps track of what parts of the screen have been
affected.

The last line of this section draws the red line that shows you which
direction the ship is pointing.

The next section of the method: ::

        # show fuel/health levels on OUR ship
        if self.isOurShip:
            dirtyrect.union_ip(pygame.draw.line(screen, red, (x+5,y),
                (x+5,y-20*(self.wlevel/self.wmax)),3))
            dirtyrect.union_ip(pygame.draw.line(screen, green, (x+10,y),
                (x+10,y-20*(self.flevel/self.fmax)),3))
            dirtyrect.union_ip(pygame.draw.line(screen, blue, (x+15,y),
                (x+15,y-20*(self.slevel/self.smax)),3))
        return [dirtyrect]

This section executes if the ship object is *our* ship. The first line
checks to see if self.isOurShip is True. If it is, then the following
lines execute. These lines are responsible for drawing the fuel level
bars over the icon.

The very last line returns a rectangle object (dirtyrect) that summarizes
all parts of the screen that were affected by updating this object. The
code that calls this method will use that information to efficiently
update the screen.

We are going to focus our attention on the first half of the method.
Since our modification will create a rotating icon, we don't need to
draw the red line over the icon. So delete this line: ::

        dirtyrect.union_ip(pygame.draw.line(screen, red, (x,y),
            (x+20*math.cos(r),y-20*math.sin(r))))


Notice that this "line" actually wraps over into two lines. Remove them
both.

Insert a blank spot in the code like this: ::

        X,r,Xlist = self.forecastPosition(displaytime-self.timestamp)
        x,y = map(int,self.client.gameToScreenCoordinates(X))

        shiprect = self.rect.move(x-self.rect[2]/2, y-self.rect[3]/2)
        dirtyrect = screen.blit(self.image, shiprect)


Then insert the following code in the gap: ::

        rdegrees = round(math.degrees(r)) % 360
        if self.imagecache.has_key(rdegrees):
            rotatedimage = self.imagecache[rdegrees]
        else:
            rotatedimage = pygame.transform.rotate(self.image, rdegrees)
            self.imagecache[rdegrees] = rotatedimage

The first of the new lines converts the angular position of the ship
to degrees (from radians) and rounds it to an integer number in the range
of 0 to 359 degrees. Notice that the % operator is being used to calculate
a remainder here!

The next line checks to see if we've already rotated an image to this angle
and if so, sets rotatedimage equal to the saved image. Otherwise (else:),
we use the pygame.transform.rotate function to rotate self.image by
the angle rdegrees and then save it in the self.imagecache using the
angle (rdegrees) as the name or key that we'll retrieve it with later.

Next, modify the following lines so that they look like this: ::

        shiprect = self.rect.move(
            x-rotatedimage.get_width()/2, y-rotatedimage.get_height()/2)
        dirtyrect = screen.blit(rotatedimage, shiprect)

This is just like the old code, except we're using the rotatedimage that
we generated (or looked up).

OK. Save the code and give it a go!