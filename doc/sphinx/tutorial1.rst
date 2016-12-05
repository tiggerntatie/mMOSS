.. _tutorial1:

mMOSS Tutorial 1: Basic Modifications
=====================================

The first **mMOSS** tutorial assumes that you have installed the development
environment for your system, including Bazaar, Pygame and a programmer's
editor or IDE (integrated development environment) like PyCharm.

Getting mMOSS Source Code
-------------------------

Open a terminal or console window and create a directory in which to
download the **mMOSS** project files, then "cd" into it. For example (Mac OSX): ::

    mkdir development
    cd development

Next, download the **mMOSS** source files using the Bazaar version control
system: ::

    bzr branch lp:mmoss

This will load source files into the **mmoss** sub-directory. "cd" into it
and get a list of the files there: ::

    cd mmoss
    ls


Test The Code
-------------

You can test the recently downloaded code by creating a server and
client on your development machine. First you will need to run the
**mMOSS** server: ::

    python mmoss-ex.py -s

This executes the **mMOSS** system and the "-s" argument tells the program
that it should run as a server and wait for one or more players to connect
to it over the network.

Open a second terminal or console window and "cd" to the mmoss folder
as before. Now type the following to run a default **mMOSS** client: ::

    python mmoss-ex.py

Executing mmoss-ex.py without any arguments will cause it to assume that it
is a client program (the version that a human player interacts directly
with) and connect it to a server running on the same machine as the client.

Python may make some minor complaints about the program as you run it,
but in the end the mMOSS game screen should appear.

The mMOSS Client Example
------------------------

The mmoss-ex.py is an *example* of a **mMOSS** client program, provided to
give *you* ideas and a starting point for creating your *own* version
of the mMOSS client program. The best way to get started with this is to
make a copy of the sample program. From the terminal prompt: ::

    cd mmoss
    cp mmoss-ex.py mymmoss.py


Now you can run your "new" version of the **mMOSS** client by typing: ::

    python mymmoss.py

This example game client is pretty ugly and pretty simple. It is intended
to be playable, but not much to look at. You are in control of a single
spaceship which you can control with the following keys:

* **W** - Thrust forward
* **A** - Rotate counter clockwise
* **D** - Rotate clockwise
* **S** - Thrust in reverse (backwards)
* **Space** - Fire your weapon
* **Q** - Quit

Notice that your ship doesn't actually rotate! Instead, your direction is
shown with a small red line that rotates when you press the **A** or
**D** keys.

The program can be halted by pressing **Q** from within the game, or by
pressing the CTRL-C key combination from the terminal window.

You can also *debug* mymmoss.py using the PyCharm editor/debugger.

Modifying mymmoss.py
--------------------

The file that you copied to make mymmoss.py is not the entire mMOSS program.
In fact, it is a relatively small portion of it. The file you have copied
is *intended* to be modified by people who want to make their own
**mMOSS** game client. These tutorials will describe a series of fairly
simple modifications that you can make to the game. Ready? Let's go!

First of all, if this is supposed to be a *space shooter* it really should
look like it's taking place in outer space. The background really ought
to be black instead of white. Let's see what it'll take to fix that.

Your mymmoss.py program file should be open inside PyCharm.

The background is already white, so we will search mymmoss.py for all
instances of the word: "white". Press CTRL-F to open a search (Find)
control in the editor. Type **white** to begin searching. PyCharm should
find and show you two places in the code where the word "white" appears: ::

    white = 255, 255, 255

and: ::

    self.background = white

The first hit occurs near the start of the file and is actually a line of
code that defines what "white" will mean in this program. It assigns
a series of three numbers (called a "tuple") to the global (meaning
it can be used everywhere in this file) variable named "white". These
three numbers refer to the Red, Green and Blue parts of the color. Since
white is the presence of all frequencies of light, it includes the
maximum values (255 is the highest possible) for each in its definition.

If you look a few lines below the definition of white you should find
a definition for black too. This one lists the three numbers: 0, 0, 0 to
indicate that black is the *absence* of any light (no red, green or blue
light is present).

The second search hit for "white" occurs in the body of an
*__init__ method* for the Client
class definition. The Client class definition contains the code that makes
this client "work". It is based (inherits code) from a parent class called
MMOSSClient, which is defined in a different file that you are not
supposed or expected to modify.

Find the line that reads: ::

    self.background = white

and delete the word "white" then replace it with "black". Note that we can't
choose just *any* color word here: if we choose to define a new color,
we should include that definition with the list of other colors at the
beginning of the file. When you're done, the line should say: ::

    self.background = black

Run/Debug.. the program again to see if the appearance has changed.

Asteroids: Houston, We Have a Problem..
---------------------------------------

The screen of your game should now be black, but what happened to the
asteroids (those black circles that used to bounce around the screen)?

The problem is that those asteroids were drawn using **black** lines, which
don't show up on this black background any more! To fix that we will have
to find the code that draws asteroids on the screen.

Press CTRL-F and search for **black**. Your search should turn up these
lines: ::

            dirtyrect = pygame.draw.line(screen, black, (x,y),
                (x+self.radius*math.cos(r),y-self.radius*math.sin(r)))
            dirtyrect.union_ip(
                pygame.draw.circle(screen, black, (x, y), self.radius, 1))

For now, don't worry about what all of this means. Just focus on the word
black that appears on these lines, which are found in the *body* of
an Asteroid class method definition called **displaySingleObject**. Try changing
those words from "black" to "white", then run the game again. Now you
should see white asteroids floating on a black background!