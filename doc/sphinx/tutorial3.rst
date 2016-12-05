.. _tutorial3:

mMOSS Tutorial 3: Change Ship Appearance
========================================

If you finished :ref:`tutorial2` then you saw how to make **mMOSS** rotate
ship icons on screen. You may have already experimented with changing the
image icons. If not, this tutorial will show you how to do that.

Create Your Own Ship Icon
-------------------------

The basic mmoss-ex.py code does not override the default size (20 pixels)
of a player ship. Accordingly, the icon size is approximately 40 pixels wide.

If you would like to create a new ship icon you should first decide how large
the ship will be. There is a limit to how large the icon can be, which
is determined by the largest message that the network subsystem
can deliver. Try to keep your icon under 100 pixels wide.

A good program for *creating* ship icons is Inkscape (http://inkscape.org/).
Following are general steps for creating your own icon:

#.  Draw a circle with a diameter that approximates the size of the ship
    you want to create. Keep in mind that the default ships in mmoss-ex.py
    are approximately 40 pixels wide.

#.  Draw filled rectangles, ovals or triangles, etc. to define the shape
    and structure of your ship. Generally try to keep everything inside the
    circle that defines your ship size.

#.  Your ship should be drawn *pointing to the right*. The reference for
    angles in mMOSS is always aligned with the positive x-axis (as it is in
    trigonometry on the unit circle).

#.  When your drawing is complete, remove the original circle (which is used
    as a drawing guide only).

#.  Save your drawing.

#.  Export your drawing to png (file/export bitmap...). The background will
    automatically be written
    as transparent, which is what you want. If your image is *not* the correct
    size you can override the final size of the png at this stage.

See an example image here:

.. image:: tutorial3-img.png

And the Inkscape :download:`svg file <tutorial3-img.svg>` used to create it.

Use an Existing Image
---------------------

You can use a downloaded image to create your icon, but beware of a few
things:

*   Most images were never intended to be a game sprite. They don't have
    sharp boundary edges or transparent areas.
*   Don't use any image unless its author has given you permission to, or
    unless the author has placed the image in the public domain.
*   If these points don't deter you, then use an image manipulation
    program (such as Gimp) to resize the image and erase areas that
    should be transparent.

Change the Ship in mMOSS
------------------------

The mmoss-ex.py program is actually designed to allow the user to select
a custom ship image from the command line. In this tutorial, however,
we will "hard code" the image file name in the code.

Use Inkscape and/or Gimp to create or download and modify a ship icon. Try
making an icon that is somewhat larger or smaller than the default images
included with mmoss-ex.py.

The ship image should be saved as a .png file in the mmossfiles subdirectory.

Load the New Ship Image
+++++++++++++++++++++++

Locate the following line in your source code: ::

    class Client(MMOSSClient):

This is the class declaration for the Client object that represents data
and code for running your game client (it keeps lists of Ship, Bullet
and Asteroid objects, talks to the server and interprets your keyboard
commands). The **Client** class really is the heart and soul of your game
client.

Below this line is the __init__ method for the class, which initializes
variables used in the class. Each variable is named self.<something>. The
"self" in front of the name means that the variable will be usable inside
any method defined in the Client. If you create or use a variable *without*
saying "self." in front of it, then the variable only will work inside the
method where you created it.

Find the line that says something like: ::

    self.shipimage = pygame.image.load("mmossfiles/"+
        self.arguments.ship_image+".png")

You may have already modified this line to load a different image. In
any case, change the line to look like this: ::

    self.shipimage = pygame.image.load("mmossfiles/mmossship.png")

Change the file name "mmossship.png" to match the file name that you saved
your new ship image to (e.g. "mmossfiles/my-scary-ship.png")

Tell the Server How Big It Is
+++++++++++++++++++++++++++++

Your ship image file might have a ship that is 60 pixels across, but the
default ship size as far as the server is concerned is 40 pixels across.
The server uses this size to figure out how massive your ship is and how
much overall fuel capacity it has. We need to tell the game server how
big *your* new ship is.

If, for example, your new ship icon is 60 pixels across, you should tell
the server that your ship has a radius of 30 (60 divided by 2).

In your source code, look for this line: ::

    def sendJoinRequest(self):

This method is called by the mMOSS framework after your game client
successfully connects to the game server. The code looks like this: ::

    def sendJoinRequest(self):
        """Create a new ship object and send a join request to the server.
        """
        super(Client,self).sendJoinRequest()
        self.myshipobject = Ship(
            client=self,
            wmax=40,
            fmax=30,
            smax=30,
            image=self.shipimage,
            objectname=self.playername,
            isourship=True)
        self.protocol.sendClientJoinRequest(self.myshipobject, self.joinResponse)

The first thing the code does is call the sendJoinRequest method in the
parent (MMOSSClient) class. Next, we create a ship object and save it
as self.myshipobject. The ship is created with a call to Ship(). The
arguments inside the parentheses are spread out over several lines, and
each is separated by a comma. The lines: ::

            wmax=40,
            fmax=30,
            smax=30,

determine the relative sizes of the **weapon**, **fuel** and **shield**
fuel tanks. The numbers given should add up to 100.

The next lines assign an image for our ship, the player name (which
defaults to the computer name) and whether the ship we are creating
represents **our** ship (which it does here).

Since you are creating your *own* new ship, you should feel free to play
around with wmax, fmax and smax.

Now we will add a new parameter to this list. Insert a space in the argument
list: ::

    client=self,
    wmax=40,
    fmax=30,
    smax=30,

    image=self.shipimage,

Then insert this new line in the gap: ::

    radius=30,

This line tells the server how big it should consider your ship to be.
The server uses this size to determine the mass and overall fuel capacity
of your ship and also how big it is for collision detection.

**There is nothing at the server that checks to see if your image size
actually matches the radius that you give here!** Entering misleading sizes
or ship images is one possible strategy for winning the mMOSS game!

If you would like your ship image to match what the server thinks your
ship size is then set the radius number to be approximately 1/2 the width
of the ship image.
