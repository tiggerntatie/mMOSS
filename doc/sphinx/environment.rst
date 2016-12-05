.. mMOSS Development Environment

=================================
mMOSS Development Environment
=================================

Introduction
============

If you want to write or debug mMOSS code, or develop a client program, you 
will need to have several things installed on your computer. Some of these
are recommended and others are required. All of these programs and libraries
together are referred to as the "development environment."

Many of the programs referred to below are available directly over the
Internet.

Recommended Software
====================

PyCharm
-------

In order to modify source files for the mMOSS system you will need a good
programmer's text editor and debugger, also known as an IDE (Integrated
Development Environment). One IDE that works very well on Linux, Windows
and Mac OSX systems is PyCharm, available from
http://www.jetbrains.com/pycharm/

Hanover High School has a classroom license to use PyCharm. Please see your
instructor for a copy of the license.

jEdit
-----

An alternative editor is jEdit, available as a free
download from http://www.jedit.org/ for all platforms or use your package
manager (Linux).

Common Required Software (OSX, Windows, Linux)
==============================================

The following tools are common to all platforms (Mac, Windows, Linux) and 
should be downloaded directly from the Internet or installed using your
system's software package system (e.g. Synaptic).

Bazaar
------

Source code for the mMOSS project is stored at 
http://launchpad.net/mmoss. The Bazaar version control 
system is required to access the current source code 
directly over the Internet. Visit 
http://bazaar.canonical.com/en/ to download the version that 
is appropriate for your computer

Python 2.6     
----------

mMOSS is written to use the Python computer language. The
latest version available is 3, but this will not be 
compatible with the Pygame and Twisted libraries that
mMOSS depends on. mMOSS is currently developed on 
Python 2.6. Visit http://python.org/ to download this version
for your computer.

Note: Python 2.6 is included with the OSX 10.6, so you won't
need to install it yourself.

Mac OSX
=======

XCode (OSX 10.5 and lower)
--------------------------

Install the version of XCode that is appropriate for your OSX version. XCode
is included on the OS installation disk or may be downloaded from Apple.


Mac OSX and Windows
===================

setuptools
------------

Visit http://pypi.python.org/pypi/setuptools and install the version of 
setuptools that is appropriate for your system and Python 2.6.

Mac OSX
+++++++

To install the downloaded file under OSX, execute the following at a 
terminal prompt: ::

    sh setup*

Windows
+++++++

To install the downloaded file under Windows, execute the installer. You 
will also need to adjust your user path from the system environment
variables dialog: ::

	%PATH%;c:\python26\scripts;c:\python26



Mac OSX (10.5 and lower) and Windows
++++++++++++++++++++++++++++++++++++

From a terminal or command prompt: ::

	easy_install pygame
	easy_install twisted
	easy_install numpy
	easy_install argparse


Mac OSX 10.6
++++++++++++

Visit http://pygame.org/download.shtml and download/install
pygame-1.9.2pre-py2.6-macosx10.6.mpkg

Next, from a terminal window type: ::

    easy_install argparse

Linux (Ubuntu, etc.)
====================

Use your system package manager to install *python-argparse*, *python-pygame*,
*python-numpy* and *python-twisted*


Obtaining the mMOSS Source Code
===============================

From a command line (or terminal window), install the current stable
mMOSS source code. Type: ::
	
	bzr branch lp:mmoss

To install the current development branch of the mMOSS source code (bleeding
edge!): ::
	
	bzr branch lp:~ericd-netdenizen/mmoss/dev

The demonstration mMOSS program can be executed by navigating into the mmoss
or dev directory and typing: ::
	
	python mmoss-ex.py -a netdenizen.org

This will launch the client (game) program and connect you to the server at
netdenizen.org. If this server is not running, you will need to open a second
terminal window and launch your own server first: ::
	
	python mmoss-ex.py -s

And then in the other terminal window, execute the game program without
any arguments: ::
	
	python mmoss-ex.py


