###
# Copyright (c) 2013, Thomas Scott
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.registry as registry
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Administration')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Administration', True)


Administration = conf.registerPlugin('Administration')
conf.registerGlobalValue(Administration, 'public',
    registry.Boolean(True, """Determines whether this plugin is publicly
    visible."""))
conf.registerGlobalValue(Administration, 'quitMsg',
    registry.String('', """Determines what quit message will be used by default.
    If the quit command is called without a quit message, this will be used.  If
    this value is empty, the nick of the person giving the quit command will be
    used."""))

conf.registerGroup(conf.supybot.commands, 'renames', orderAlphabetically=True)



# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
