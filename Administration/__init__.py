###
# Copyright (c) 2013, Thomas Scott
# All rights reserved.
#
#
###

"""
Provides commands useful to the admins of the bot; the commands here require
their caller to have the 'admin' capability.
"""

import supybot
import supybot.world as world

# Use this for the version of this plugin.  You may wish to put a CVS keyword
# in here if you\'re keeping the plugin in CVS or some similar system.
__version__ = "%%VERSION%%"

__author__ = supybot.authors.jemfinch

# This is a dictionary mapping supybot.Author instances to lists of
# contributions.
__contributors__ = {}

from . import config
from . import plugin
reload(plugin) # In case we're being reloaded.

if world.testing:
    from . import test

Class = plugin.Class
configure = config.configure


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
