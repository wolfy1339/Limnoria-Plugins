###
# Copyright (c) 2013-2015, wolfy1339
# All rights reserved.
#
#
###

from supybot.test import *

class AdministrationTestCase(PluginTestCase):
    plugins = ('Administration',)
    def testLoad(self):
        self.assertError('load Owner')
        self.assertError('load owner')
        self.assertNotError('load Channel')
        self.assertNotError('list Owner')

    def testReload(self):
        self.assertError('reload Channel')
        self.assertNotError('load Channel')
        self.assertNotError('reload Channel')
        self.assertNotError('reload Channel')

    def testUnload(self):
        self.assertError('unload Foobar')
        self.assertNotError('load Channel')
        self.assertNotError('unload Channel')
        self.assertError('unload Channel')
        self.assertNotError('load Channel')
        self.assertNotError('unload CHANNEL')

    def testDisable(self):
        self.assertError('disable enable')
        self.assertError('disable identify')

    def testEnable(self):
        self.assertError('enable enable')

    def testEnableIsCaseInsensitive(self):
        self.assertNotError('disable Foo')
        self.assertNotError('enable foo')

    def testRename(self):
        self.assertError('rename Admin join JOIN')
        self.assertError('rename Admin join jo-in')
        self.assertNotError('rename Admin join testcommand')
        self.assertRegexp('list Admin', 'testcommand')
        self.assertNotRegexp('list Admin', 'join')
        self.assertError('help join')
        self.assertRegexp('help testcommand', 'Tell the bot to join')
        self.assertRegexp('join', 'not a valid command')
        self.assertHelp('testcommand')
        self.assertNotError('unrename Admin')
        self.assertNotRegexp('list Admin', 'testcommand')

    @skip('Nested commands cannot be renamed yet.')
    def testRenameNested(self):
        self.assertNotError('rename Admin "capability remove" rmcap')
        self.assertNotRegexp('list Admin', 'capability remove')
        self.assertRegexp('list Admin', 'rmcap')
        self.assertNotError('reload Admin')
        self.assertNotRegexp('list Admin', 'capability remove')
        self.assertRegexp('list Admin', 'rmcap')
        self.assertNotError('unrename Admin')
        self.assertRegexp('list Admin', 'capability remove')
        self.assertNotRegexp('list Admin', 'rmcap')
 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
