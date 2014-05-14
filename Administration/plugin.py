###
# Copyright (c) 2013, Thomas Scott
# All rights reserved.
#
#
###
import gc
import os
import sys
import time
import socket
import linecache

import re

import supybot.log as log
import supybot.conf as conf
import supybot.i18n as i18n
import supybot.utils as utils
import supybot.world as world
import supybot.ircdb as ircdb
from supybot.commands import *
import supybot.irclib as irclib
import supybot.plugin as plugin
import supybot.plugins as plugins
import supybot.drivers as drivers
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.registry as registry
import supybot.callbacks as callbacks
import supybot.utils as utils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Administration')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

class Administration(callbacks.Plugin):
    """Add the help for "@plugin help Administration" here
    This should describe *how* to use this plugin."""
    threaded = True
def load(self, irc, msg, args, optlist, name):
        """[--deprecated] <plugin>

        Loads the plugin <plugin> from any of the directories in
        conf.supybot.directories.plugins; usually this includes the main
        installed directory and 'plugins' in the current directory.
        --deprecated is necessary if you wish to load deprecated plugins.
        """
        ignoreDeprecation = False
        for (option, argument) in optlist:
            if option == 'deprecated':
                ignoreDeprecation = True
        if name.endswith('.py'):
            name = name[:-3]
        if irc.getCallback(name):
            irc.error('%s is already loaded.' % name.capitalize())
            return
        try:
            module = plugin.loadPluginModule(name, ignoreDeprecation)
        except plugin.Deprecated:
            irc.error('%s is deprecated.  Use --deprecated '
                      'to force it to load.' % name.capitalize())
            return
        except ImportError, e:
            if str(e).endswith(' ' + name):
                irc.error('No plugin named %s exists.' % utils.str.dqrepr(name))
            else:
                irc.error(str(e))
            return
        cb = plugin.loadPluginClass(irc, module)
        name = cb.name() # Let's normalize this.
        conf.registerPlugin(name, True)
        irc.replySuccess()
        load = wrap(load, [getopts({'deprecated': ''}), 'something'])

def reload(self, irc, msg, args, name):
        """<plugin>

        Unloads and subsequently reloads the plugin by name; use the 'list'
        command to see a list of the currently loaded plugins.
        """
        callbacks = irc.removeCallback(name)
        if callbacks:
            module = sys.modules[callbacks[0].__module__]
            if hasattr(module, 'reload'):
                x = module.reload()
            try:
                module = plugin.loadPluginModule(name)
                if hasattr(module, 'reload') and 'x' in locals():
                    module.reload(x)
                if hasattr(module, 'config'):
                    reload(module.config)
                for callback in callbacks:
                    callback.die()
                    del callback
                gc.collect() # This makes sure the callback is collected.
                callback = plugin.loadPluginClass(irc, module)
                irc.replySuccess()
            except ImportError:
                for callback in callbacks:
                    irc.addCallback(callback)
                irc.error('No plugin %s exists.' % name)
        else:
            irc.error('There was no plugin %s.' % name)
    reload = wrap(reload, ['something'])

    def unload(self, irc, msg, args, name):
        """<plugin>

        Unloads the callback by name; use the 'list' command to see a list
        of the currently loaded plugins.  Obviously, the Owner plugin can't
        be unloaded.
        """
        if ircutils.strEqual(name, self.name()):
            irc.error('You can\'t unload the %s plugin.' % name)
            return
        # Let's do this so even if the plugin isn't currently loaded, it doesn't
        # stay attempting to load.
        conf.registerPlugin(name, False)
        callbacks = irc.removeCallback(name)
        if callbacks:
            for callback in callbacks:
                callback.die()
                del callback
            gc.collect()
            irc.replySuccess()
        else:
            irc.error('There was no plugin %s.' % name)
    unload = wrap(unload, ['something'])

def _loadPlugins(self, irc):
        self.log.info('Loading plugins (connecting to %s).', irc.network)
        alwaysLoadImportant = conf.supybot.plugins.alwaysLoadImportant()
        important = conf.supybot.commands.defaultPlugins.importantPlugins()
        for (name, value) in conf.supybot.plugins.getValues(fullNames=False):
            if irc.getCallback(name) is None:
                load = value()
                if not load and name in important:
                    if alwaysLoadImportant:
                        s = '%s is configured not to be loaded, but is being '\
                            'loaded anyway because ' \
                            'supybot.plugins.alwaysLoadImportant is True.'
                        self.log.warning(s, name)
                        load = True
                if load:
                    # We don't load plugins that don't start with a capital
                    # letter.
                    if name[0].isupper() and not irc.getCallback(name):
                        # This is debug because each log logs its beginning.
                        self.log.debug('Loading %s.', name)
                        try:
                            m = plugin.loadPluginModule(name,
                                                        ignoreDeprecation=True)
                            plugin.loadPluginClass(irc, m)
                        except callbacks.Error, e:
                            # This is just an error message.
                            log.warning(str(e))
                        except (plugins.NoSuitableDatabase, ImportError), e:
                            s = 'Failed to load %s: %s' % (name, e)
                            if not s.endswith('.'):
                                s += '.'
                            log.warning(s)
                        except Exception, e:
                            log.exception('Failed to load %s:', name)
                else:
                    # Let's import the module so configuration is preserved.
                    try:
                        _ = plugin.loadPluginModule(name)
                    except Exception, e:
                        log.debug('Attempted to load %s to preserve its '
                                  'configuration, but load failed: %s',
                                  name, e)
        world.starting = False

def disable(self, irc, msg, args, plugin, command):
        """[<plugin>] <command>

        Disables the command <command> for all users (including the owners).
        If <plugin> is given, only disables the <command> from <plugin>.  If
        you want to disable a command for most users but not for yourself, set
        a default capability of -plugin.command or -command (if you want to
        disable the command in all plugins).
        """
        if command in ('enable', 'identify'):
            irc.error('You can\'t disable %s.' % command)
            return
        if plugin:
            if plugin.isCommand(command):
                pluginCommand = '%s.%s' % (plugin.name(), command)
                conf.supybot.commands.disabled().add(pluginCommand)
                plugin._disabled.add(command)
            else:
                irc.error('%s is not a command in the %s plugin.' %
                          (command, plugin.name()))
                return
        else:
            conf.supybot.commands.disabled().add(command)
            self._disabled.add(command)
        irc.replySuccess()
    disable = wrap(disable, [optional('plugin'), 'commandName'])

    def enable(self, irc, msg, args, plugin, command):
        """[<plugin>] <command>

        Enables the command <command> for all users.  If <plugin>
        if given, only enables the <command> from <plugin>.  This command is
        the inverse of disable.
        """
        try:
            if plugin:
                plugin._disabled.remove(command, plugin.name())
                command = '%s.%s' % (plugin.name(), command)
            else:
                self._disabled.remove(command)
            conf.supybot.commands.disabled().remove(command)
            irc.replySuccess()
        except KeyError:
            irc.error('That command wasn\'t disabled.')
    enable = wrap(enable, [optional('plugin'), 'commandName'])

    def rename(self, irc, msg, args, plugin, command, newName):
        """<plugin> <command> <new name>

        Renames <command> in <plugin> to the <new name>.
        """
        if not plugin.isCommand(command):
            what = 'command in the %s plugin' % plugin.name()
            irc.errorInvalid(what, command)
        if hasattr(plugin, newName):
            irc.error('The %s plugin already has an attribute named %s.' %
                      (plugin, newName))
            return
        registerRename(plugin.name(), command, newName)
        renameCommand(plugin, command, newName)
        irc.replySuccess()
    rename = wrap(rename, ['plugin', 'commandName', 'commandName'])

    def unrename(self, irc, msg, args, plugin):
        """<plugin>

        Removes all renames in <plugin>.  The plugin will be reloaded after
        this command is run.
        """
        try:
            conf.supybot.commands.renames.unregister(plugin.name())
        except registry.NonExistentRegistryEntry:
            irc.errorInvalid('plugin', plugin.name())
        self.reload(irc, msg, [plugin.name()]) # This makes the replySuccess.
    unrename = wrap(unrename, ['plugin'])

Class = Administration


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
