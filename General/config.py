###
# Copyright (c) 2011, Anthony Boot
# Copyright (c) 2015, wolfy1339
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

conf.registerChannelValue(General, 'youtubeSnarfer',
                          registry.Boolean(False, """Determines if this plugin will snarf youtube links,
with the video's name and information"""))

conf.registerChannelValue(General, 'pasteSnarfer',
                          registry.Boolean(False, """Determines if this plugin will snarf pastebin links,
with the paste's name,owner,syntax"""))

conf.registerChannelValue(General, 'enableMooReply',
                          registry.Boolean(False, """Determines if this plugin will respond to moo's
sent by a user"""))

conf.registerChannelValue(General, 'enableGreeter',
                          registry.Boolean(False, """Determines if this plugin will greet users, when
they say hi, or other similar expressions"""))

conf.registerChannelValue(General, 'enableAwayMsgKicker',
                          registry.Boolean(False, """Determines if this plugin will kick users
when they send an away message to the channel"""))

conf.registerChannelValue(General, 'enableUserCorrect',
                          registry.Boolean(False, """Determines if this plugin will let users correct themselves
using this plugin"""))
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
