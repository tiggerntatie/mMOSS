.. _tutorial8:

mMOSS Tutorial 8: Wait... What? Which Bar is Which?
===================================================

Now that you have three nice, big colored fuel bars on your screen,
it would be nice if you could remember which bar stood for which kind
of "fuel". Would that be easier to figure out if each bar had its meaning
overlaid on it in text?


Revise the HealthPanel
----------------------

The HealthPanel class that you created in :ref:`tutorial7` will provide
a good place for us to make some changes and add some text, but it might
be useful to rewrite it a little bit. First we'll add a few definitions
at the beginning of the HealthPanel __init__ method: ::

        self.BARHEIGHT = 60
        self.BARWIDTH = 20
        self.BARX = [10, 35, 60]
        self.BARY = self.client.screensize[1]-self.BARHEIGHT/2

These new member variables will be used to control the size and placement
of the fuel bars in the rest of the code. Add these lines at the end of
the HealthPanel __init__ method.

Next we'll add some more code to the __init__ method (just tack it on to
the end) that will generate the actual text: ::

        self.font = pygame.font.Font("freesansbold.ttf", 15)
        self.healthtexts = [pygame.transform.rotate(
            self.font.render(text, 1, black),90) for text in
            ['weapon', 'fuel', 'shield']]
        self.healthrects = [text.get_rect() for text in self.healthtexts]
        for rect, x in zip(self.healthrects, self.BARX):
            rect.center = (x, self.BARY)

Let's look at this bit, line by line: The first line loads the font file.
The freesansbold.ttf font is included in Pygame so you don't have to find
a font of your own.

Next self.healthtexts is used to store a list of rotated and rendered text
images (weapon, fuel and shield) that are generated in a list comprehension.
Then a list of rectangles is generated from the healthtexts.

Finally, the rectangle centers are set using a **for:** loop. The **for:**
loop "zips" the list of healthrects and the bar X positions (BARX) into a
list of rectangle, X position tuples (don't worry if this sounds like
gibberish right now). The final line sets the center position of each
text rectangle so that their centers are all at the same height.

So.. basically what this __init__ code does is create the text images that
we'll use when the HealthPanel gets redrawn with each screen refresh.

Modify the HealthPanel displaySingleObject Method
+++++++++++++++++++++++++++++++++++++++++++++++++

Next, find the following piece of code in the displaySingleObject
method: ::

                (x+xpos,y-BARHEIGHT*(level/maxlvl)),10) for
            color, xpos, level, maxlvl in
                [[red, 5, ship.wlevel, ship.wmax],
                [green, 20, ship.flevel, ship.fmax],
                [blue, 35, ship.slevel, ship.smax]]]

Change BARHEIGHT to self.BARHEIGHT (because it is now defined in the __init__
method). Change "10" to self.BARWIDTH. Change "5" to self.BARX[0], "20" to
self.BARX[1] and "35" to self.BARX[2].

Now add the following code near the end of and *just before the return
statement* in the displaySingleObject method: ::

        dirtyrects.extend([screen.blit(text,rect) for
            text, rect in zip(self.healthtexts, self.healthrects)])

This line will copy all of the text images (self.healthtexts and
self.healthrects) onto the screen (using screen.blit()). Notice that the
beginning of the line, usedrects.extend(, is used to keep track of which
parts of the screen have been changed, so the display manager can
efficiently update the screen.

Now What?
---------

Run and test your updated code. You should have a text message overlaid
on each fuel bar in the corner of your screen. Where else could you
try using some text?

*   Display player names on top of ship images.
*   Display player stats on screen instead of the console.
*   Display your ship operating mode (custom weapon settings, etc.) on the
    screen.
*   Display tactical information about the locations of other players.

The HealthPanel is an example of using a piece of the screen "real estate"
to display some information. You could use another corner of the screen
to display a mini-map or radar view of the entire playing area. This would
be an interesting and challenging modification with several things to
consider:

*   You would only want to show the ships and possibly asteroids, but not
    any of the bullets.
*   The Client class knows about `self.objectlist`, which contains a list
    of every object in the game (including bullets).
*   You can figure out what kind of objects are in self.objectlist by
    using code like this: `if type(obj) is Ship:`
