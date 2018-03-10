###
# Copyright (c) 2014-2016, wolfy1339
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
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import json
try:
    from supybot.i18n import PluginInternationalization
    from supybot.i18n import internationalizeDocstring
    _ = PluginInternationalization('UserInfo')
except ImportError:
    _ = lambda x: x
    internationalizeDocstring = lambda x: x


@internationalizeDocstring
class UserInfo(callbacks.Plugin):
    """A plugin that fetches member information from the BMN website"""
    threaded = True

    @internationalizeDocstring
    @wrap([optional('somethingWithoutSpaces')])
    def records(self, irc, msg, args, user):
        """[<memberName>]

        Returns user information from their record.
        If <memberName> isn't given, return the
        record of the person giving the command.
        """
        if user:
            self._getMemberInfo(irc, user)
        else:
            self._getMemberInfo(irc, msg.nick)

    @urlSnarfer
    def UserInfoSnarfer(self, irc, msg, args, match):
        r"http://brilliant-minds.tk/members.html\?([\w-]+)|@([\w-]+)"
        name = match.group(1) or match.group(2)
        self.log.debug('UserInfo: Snarfer Group 1' + match.group(1))
        self.log.debug('UserInfo: Snarfer Group 2' + match.group(2))
        self.log.debug('UserInfo: Snarfer Group 0' + match.group(0))

        if msg.args[1].startswith('Member {0}:'.format(name)):
            return  # Don't respond to other bots with this plugin loaded

        if self.registryValue('MemberSnarfer', msg.args[0]):
            self._getMemberInfo(irc, name)
        else:
            return

    @internationalizeDocstring
    @wrap
    def members(self, irc, msg, args):
        """No arguments

        Returns the current members list in a private message if not in #BMN"""

        jsonUrl = 'http://brilliant-minds.tk/members.json'
        jsonFile = utils.web.getUrl(jsonUrl)
        data = json.loads(jsonFile.decode(utils.web.getEncoding(jsonFile) or 'utf8', 'replace'))
        officers = 'Officers\n'
        officers += '------------\n'
        officers += ','.join(i[1] + ' ' + i[0] for i in data['officers'])

        enlisted = 'Enlisted\n'
        enlisted += '------------\n'
        enlisted += ','.join(i[1] + ' ' + i[0] for i in data['enlisted'])

        preofficers = 'Preofficers\n'
        preofficers += '------------\n'
        preofficers += ','.join(i[1] + ' ' + i[0]
                                for i in data['preofficers'])

        message = '\n\n'.join((officers, enlisted, preofficers))

        if self.registryValue('enableMembersListInChannel', msg.args[0]):
            irc.reply(message, nickPrefix=False)
        else:
            irc.reply(message, private=True)

    def _getMemberInfo(self, irc, user):
        if (not user.startswith('http://') and
                not user.startswith('https://')):
            userName = user
        else:
            userName = user.split('members.html?')[1]

        url = 'http://brilliant-minds.github.io/members/{0}.json'.format(userName)
        try:
            jsonFile = utils.web.getUrl(url)
        except utils.web.Error:
            irc.error(
                _('User {0} isn\'t in my database, sorry.'.format(userName)), Raise=True)

        userData = json.loads(jsonFile.decode(utils.web.getEncoding(jsonFile) or 'utf8', 'replace'))
        awards = []
        rank = []
        rank.append(userData['rank'])
        rank.append(userData['rank_comment'])

        values = ['Badge', 'Standard', 'Bronze',
                      'Silver', 'Gold', 'Diamond']
        for award, value in list(userData['awards'].items()):
            if values[value] == 'Badge':
                awards.append('{0} {1}'.format(award, values[value]))
            else:
                awards.append('{0}: {1}'.format(award, values[value]))
        awards = ', '.join(awards)

        if userData['voucher']:
            status = 'This member has a voucher'
            if userData['safe'] == 1:
                status += ' and is safe for the next IMC/IRC'
            elif userData['safe'] == 2:
                status += ' and is autosafe'
        else:
            if userData['safe'] == 1:
                status = 'This member is safe for the next IMC/IRC'
            elif userData['safe'] == 2:
                status = ' '.join(['This member is absolutely necessary',
                                   'to keep the group going and thus is autosafe'])

        irc.reply(('Member {0}: {1}, {2} | {3} | '
                   'http://brilliant-minds.tk/members.html?{0} | Awards {4}'
                   ).format(userName, rank[0], rank[1], status, awards),
                  prefixNick=False)
        self.log.info('UserInfo: Member {0} found'.format(userName))

Class = UserInfo

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
