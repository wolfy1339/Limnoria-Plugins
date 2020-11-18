###
# Copyright (c) 2011, AntB
# Copyright (c) 2015-2016, wolfy1339
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#    this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions, and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#    contributors to this software may be used to endorse or promote products
#    derived from this software without specific prior written consent.
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

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import supybot.ircmsgs as ircmsgs
import json
import random
import re


class Powder(callbacks.PluginRegexp):
    """Contains all sorts of random stuff."""
    threaded = True
    unaddressedRegexps = ['powderSnarfer', 'forumSnarfer']

    def browse(self, irc, msg, args, ID):
        """<SaveID>

            Returns information about a save."""
        self._getSaveInfo(irc, ID)
    browse = wrap(browse, ['somethingWithoutSpaces'])

    @urlSnarfer
    def powderSnarfer(self, irc, msg, match):
        r"http://powdertoy.co.uk/Browse/View.html\?ID=([0-9]+)|^[~]([0-9]+)|http://tpt.io/~([0-9]+)|http://powdertoy.co.uk/~([0-9]+)"
        ID = match.group(1) or match.group(
            2) or match.group(3) or match.group(4)

        if msg.args[1].startswith('Save ' + ID + ' is'):
            return  # Don't respond to save info from other bots with this plugin

        self.log.info('powderSnarfer - save URL Found ' + match.group(0))
        if self.registryValue('powderSnarfer', msg.args[0]):
            self._getSaveInfo(irc, ID)
        else:
            return

    def _getSaveInfo(self, irc, ID):
        if 'http://' in ID:
            if '~' in ID:
                ID = ID.split('~')[1]
            else:
                ID = ID.split('View.html?ID=')[1]
            urlGiven = 'http://powdertoy.co.uk/Browse/View.json?ID=' + ID
            url = ''
        else:
            urlGiven = 'http://powdertoy.co.uk/Browse/View.json?ID=' + ID
            url = 'http://tpt.io/~' + ID
        jsonFile = utils.web.getUrl(urlGiven)
        jsonFileEncoding = utils.web.getEncoding(jsonFile) or 'utf8'
        data = json.loads(jsonFile.decode(jsonFileEncoding, 'replace'))
        if data['Username'] == 'FourOhFour':
            saveMsg = 'Save ' + ID + ' doesn\'t exist.'
        else:
            saveMsg = 'Save ' + ID + ' is ' + data['Name'].replace('&#039;', '\'').replace(
                '&gt;', '>') + ' by ' + data['Username'] + '. Score: ' + str(data['Score']) + '.'
            if len(url) > 0:
                saveMsg += ' ' + url
        irc.reply(saveMsg, prefixNick=False)

    @wrap
    def frontpage(self, irc, msg, args):
        """

        Returns the front page of saves via notices - abuse will not be tolerated."""
        jsonFile = utils.web.getUrl('http://powdertoy.co.uk/Browse.json')
        jsonFileEncoding = utils.web.getEncoding(jsonFile) or 'utf8'
        data = json.loads(jsonFile.decode(jsonFileEncoding, 'replace'))['Saves']

        outMsg = ''
        x = 0
        for each in data:
            outMsg = '{0}\x02Save:\x02 {1:<24} - \x02By:\x02 {2:<14} - \x02ID: \x02{3:<6} - \x02Votes:\x02 {4:<4}'.format(
                outMsg, each['Name'].replace('&#039;', '\''), each['Username'], str(each['ID']), str(each['Score']))
            x += 1
            if x % 2 == 0:
                irc.reply(msg.nick, outMsg, private=True)
                outMsg = ''
                continue
            outMsg = '{0} -- '.format(outMsg)

    @wrap(['something'])
    def forum(self, irc, msg, num):
        """

        Returns information on a forum post."""
        self._getPostDetails(irc, msg, num)

    @urlSnarfer
    def forumSnarfer(self, irc, msg, match):
        r"http://powdertoy[.]co[.]uk/Discussions/Thread/View[.]html[?]Thread=([0-9]+)|http://tpt.io/:([0-9]+)|^:([0-9]+)"
        threadNum = match.group(1) or match.group(2) or match.group(3)
        if self.registryValue('forumSnarfer', msg.args[0]):
            self._getPostDetails(irc, msg, threadNum)
        else:
            return

    def _getPostDetails(self, irc, msg, threadNum):
        jsonFile = utils.web.getUrl('http://powdertoy.co.uk/Discussions/Thread/View.json?Thread={0}'.format(threadNum))
        jsonFileEncoding = utils.web.getEncoding(jsonFile) or 'utf8'
        data = json.loads(jsonFile.decode(jsonFileEncoding, 'replace'))
        if data.get('Status') == 0:
            return
        cg = data['Info']['Category']
        tp = data['Info']['Topic']

        irc.reply(
            'Forum post is \'%s\' in the %s section, posted by %s and has %s replies. Last post was by %s at %s' %
            (tp['Title'],
             cg['Name'],
                tp['Author'],
                tp['PostCount'] -
                1,
                tp['LastPoster'],
                tp['Date']),
            prefixNick=False)
        self.log.info(
            'FORUMSNARF: Thread %s found. %s in the %s section' %
            (threadNum, tp['Title'], cg['Name']))

    @wrap(['something'])
    def profile(self, irc, msg, args, user):
        """<username|ID>

          returns a link to the users profile and some brief information"""

        try:
            jsonFile = utils.web.getUrl('http://powdertoy.co.uk/User.json?Name={0}'.format(user))
            jsonFileEncoding = utils.web.getEncoding(jsonFile) or 'utf8'
            userData = json.loads(jsonFile.decode(jsonFileEncoding, 'replace'))
            uDu = userData['User']
            irc.reply(
                'http://powdertoy.co.uk/@{0} | Has {2} saves - Average score {3} - Highest score {4} | Posted {5} topics -  {6} posts - Has {7} reputation.'.format(
                    user,
                    None,
                    uDu['Saves']['Count'],
                    uDu['Saves']['AverageScore'],
                    uDu['Saves']['HighestScore'],
                    uDu['Forum']['Topics'],
                    uDu['Forum']['Replies'],
                    uDu['Forum']['Reputation']),
                prefixNick=False)
        except Exception as e:
            irc.error('User or ID doesn\'t exist - or something went wrong.. {0}'.format(e))

    @wrap
    def randomsave(self, irc, msg, args):
        """

        Returns a random save from powdertoy.co.uk"""
        found = False
        while found is False:
            url = utils.web.getUrl('http://powdertoythings.co.uk/Powder/Saves/Random.json?Count=1')
            encoding = utils.web.getEncoding(url) or 'utf8'
            saveID = str(json.loads(url.decode(encoding))['Saves'][0]['ID'])
            jsonFile = utils.web.getUrl('http://powdertoy.co.uk/Browse/View.json?ID={0}'.format(saveID))
            jsonFileEncoding = utils.web.getEncoding(jsonFile) or 'utf8'
            page = json.loads(jsonFile.decode(jsonFileEncoding, 'replace'))
            if page['Username'] != 'FourOhFour':
                found = True

        self._getSaveInfo(irc, saveID, 0)

    @wrap
    def comic(self, irc, msg, args):
        """

        Returns latest comic number and name."""
        try:
            try:
                data = utils.web.getUrl('http://cate.superdoxin.com/')
            except Exception:
                irc.error('Could not access comics website')
                return
            match = None
            for match in re.finditer(
                    r" href=\'http://superdoxin.com/static/cate/files/(([0-9]+)([^\']+))\'",
                    data):
                pass
            filename = match.group(1)
            num = match.group(2)
            name = match.group(3)

            irc.reply(
                'Latest comic id is {0} and is titled {1} - http://www.superdoxin.com/static/cate/files/{2}'.format(
                    num,
                    name,
                    filename))
        except Exception:
            irc.error('Comic checker is broken, use $bug comic')

Class = Powder

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
