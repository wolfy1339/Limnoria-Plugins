###
# Copyright (c) 2011, Anthony Boot
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('General', True)


General = conf.registerPlugin('General')

conf.registerGlobalValue(General, 'public',
    registry.Boolean(True, """Determines whether this plugin is publicly
visible."""))

conf.registerGlobalValue(General, 'youtubeSnarfer',
    registry.Boolean(True, """Determines if this plugin will snarf ~<saveid>,
with the save's name and information"""))
conf.registerChannelValue(General, 'youtubeSnarfer',
    registry.Boolean(True, """Determines if this plugin will snarf ~<saveid>, 
with the save's name and information"""))

conf.registerGlobalValue(General, 'pasteSnarfer',
    registry.Boolean(True, """Determines if this plugin will snarf pastebin links,
with the paste's name,owner,syntax"""))
conf.registerChannelValue(General, 'pasteSnarfer',
    registry.Boolean(True, """Determines if this plugin will snarf pastebin links,
with the paste's name,owner,syntax"""))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
