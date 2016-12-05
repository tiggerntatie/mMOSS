.. mMOSS Theory of Operation

=================================
mMOSS Theory of Operation
=================================

Introduction
============

This is the introduction to the Theory of operation.

.. If I want to include the quadratic function, I would say
    :math:`{-b \pm\sqrt{b^2-4ac}} \over {2a}`

Coordinate System
=================

The mMOSS game takes place in a finite, rectangular 2D area. When objects
or players reach the boundary of this space, they wrap back to the opposite
side.

All objects are located in this space using a conventional cartesian 
coordinate system where positive x is to the right, and positive y is up.
The origin (0,0) is located at the lower-left-hand corner of the playing area.
One unit on this system corresponds to a pixel on the computer screen.

The Pygame library and most computer graphic systems use a slightly different
coordinate system for describing screen locations. The origin (0,0) of the 
screen coordinates system is at the upper-left-hand corner of the computer
screen, with positive x to the right and positive y in the **down** direction.
Before displaying anything on the Pygame screen, mMOSS must perform a 
coordinate translation from the cartesian system to the Pygame system.

Angles in mMOSS are measured with respect to the positive x axis, 
in radians, with positive angles indicating counter-clockwise 
rotations. The Pygame library uses degrees for angle measurements and 
positive angles for counter-clockwise rotations.



