###
# Copyright (c) 2013-2015, wolfy1339
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import sys

if sys.version_info >= (2, 7, 0):
    from unittest import skip
else:
    # Workaround
    def skip(string):
        return lambda x:None
from supybot.test import *

import supybot.conf as conf
import supybot.plugin as plugin

class AdministrationTestCase(PluginTestCase):
    plugins = ('Administration', 'Config', 'Misc', 'Admin')
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
