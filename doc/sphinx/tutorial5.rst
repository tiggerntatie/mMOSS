.. _tutorial5:

mMOSS Tutorial 5: Make it BIGGER!
=================================

Up to now we have been playing the **mMOSS** game in a little tiny window
where everything wraps around when it gets to the edge. If a lot of
players are in the server at one time then things can get a little
busy. Wouldn't it be nice if the server was actually keeping track of
a much larger area?

As it turns out, the server *can* keep track of a much larger area.
Unfortunately, if you connect to a "large" server with the client you
have now you will only see a fixed window into the larger playing area.

What we really need to do is give the player a way to move the window
around the playing area.

Map Some New Keys
-----------------

We need to give the player the power to move a viewport around the playing
area. For this we need to enable some new keys: the left, right, up and
down arrow keys.

Key presses are detected and managed by a controller object. When our
code creates the controller we tell it which keys we want to
keep track of. This is done in two places:

At the top of your program file there are a list of import statements.
The import statement tells Python to look in another file for more code
or data. One line in particular: ::

    from mmoss.controller import A,S,D,Q,W,SPACE,TAB

tells Python to look in the mmoss folder for a Python source file called
controller. The list of names at the end are the names defined in controller
that *our* code would like to use. In this case it is simply a list of keys.
All we have to do is add the new keys to the list. If you would like to see
the list of *all* keys that the controller knows about, open the
controller.py file and look near the top for the key definitions.

In our case, we will add the following: ::

    LEFT, RIGHT, UP, DOWN

Just tack these on to the end of the list given in the import statement.
Don't forget to put a comma between the old list and the new.

.. note::

    If you have already added these keys and are using them for something
    else then you will have to pick another four keys for the window
    panning feature.


Tell the Controller to Look for the New Keys
++++++++++++++++++++++++++++++++++++++++++++

Now that we've imported the key names, we need to tell the controller that
we'd like to have it check for them. Look at the __init__ method of the
Client class (below the line that begins with "class Client...". This
section of code has a line that looks like this: ::

        self.controller = Controller([A,S,D,W,Q,SPACE,TAB])

Just add the list of keys (LEFT, RIGHT, etc.) in here. Again, don't forget
to add a comma before you paste in the new keys.

Do Something When the Pan Keys are Pressed
------------------------------------------

Look in the code for a comment that says "Check for user input".

Below this is a series of Client methods that look for keypresses and
do appropriate things. The first method in here is called handleControls and
it is responsible for calling all the other methods. We will create a new
method between handleControls and checkThrustControl. Position your cursor
in the white space between these methods and paste in the following (or
type it): ::

    def checkPanControls(self):
        """Handle arrow keys, used to pan the display window over the game
        area."""
        left, right, up, down = map(
            self.controller.key, (LEFT, RIGHT, UP, DOWN))
        mvx = mvy = 0
        if left and left.down: mvx=-5
        if right and right.down: mvx=5
        if up and up.down: mvy=5
        if down and down.down: mvy=-5
        self.screenrect = (self.screenrect[0]+mvx,
            self.screenrect[1]+mvy, self.screenrect[2], self.screenrect[3])

This is a brand new method called checkPanControls.

The first line following the method declaration is a special standalone
string with triple quotation marks, known as a *doc string*. These special
strings are processed by Python and can be turned into documentation for
the code. It is sort of like a super comment.

Next: if you have looked at other key handling code, you expect to see lines that
look something like ::

    left = self.controller.key(LEFT)

In the code we added we have a single line that does this for all four
panning keys: ::

        left, right, up, down = map(
            self.controller.key, (LEFT, RIGHT, UP, DOWN))

The **map** function will automatically call self.controller.key for each
of the arguments in the list that follows (LEFT, RIGHT, UP, DOWN). This
is a convenient shorthand way of doing the same thing over and over again.

The next several lines look at the state of the keys (are they pressed or
not) and adjusts the variables mvx and mvy to have the number of pixels
that we would like to move the viewport in the left/right direction (mvx)
or the up/down direction (mvy). You can make the viewport panning faster or
slower by changing the numbers to something other than 5.

The last line of the new code changes the location of the screen rectangle
by whatever mvx and mvy are. Simple!!

Last But Not Least
------------------

Now that we've added a brand new method, we'll have to make sure it gets
executed. Just add the following line at the end of the handleControls
method: ::

        self.checkPanControls()

Test your code!

.. note::

    If your server is running with default settings then it will still be
    a small playing area and the panning function will work funny. To run
    the server with a bigger area add the following parameters (for a
    1000 by 1000 playing area) to the
    script when you run it: -W 1000 -H 1000

