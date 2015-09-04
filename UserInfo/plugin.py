###
# Copyright (c) 2014-2015, wolfy1339
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
    _ = PluginInternationalization('UserInfo')
except ImportError:
    _ = lambda x:x

class UserInfo(callbacks.Plugin):
    """A plugin that fetches member information from the BMN website"""
    threaded = True
    def profile(self, irc, msg, args, user):
        """<memberName>

        Returns user information from their record"""
        self._getMemberInfo(self, irc, user)
    profile = wrap(profile,['somethingWithoutSpaces'])

    def UserInfoSnarfer(self, irc, msg, match):
        r"http://brilliant-minds.tk/members.html\?([a-zA-Z0-9_])|@([a-zA-Z0-9_])"
        Name = match.group(1) or match.group(2)

        if msg.args[1].startswith("Member is:"):
            return  # Don't respond to member info from other bots with this plugin

        if self.registryValue('MemberSnarfer') == "False":
            return
        else:
            self._getMemberInfo(self, irc, Name)

    UserInfoSnarfer = urlSnarfer(UserInfoSnarfer)

    def members(self, irc, msg, args):
        """

        Returns the current members list"""
        data = json.loads(utils.web.getUrl("http://brilliant-minds.tk/members.json"))
        officers = data["officers"]
        enlisted = data["enlisted"]
        preofficers = data["preofficers"]
 
        for member, rank in officers:

        for members, rank in enlisted:
  
        for members, rqank in preofficers:

        if irc.channel != "#BMN":
            irc.queueMsg(ircmsgs.privmsg(msg.nick, "{0}".format(data))
        else:
            irc.reply("{0}".format(data), nickPrefix=false)
    members = wrap(members)

    def _getMemberInfo(self, irc, user):
        """<username>

        returns a link to a user's profile and some information"""
        try:
            if not user.startswith("http://") and not user.startswith("https://"):
                userName = user
            else:
                if user.startswith("https://"):
                    user = user.split("https://")[0]
                userName = user.split("members.html?")[1]

            userData = json.loads(utils.web.getUrl("http://brilliant-minds.tk/members/{0}.json".format(userName)))
            Awards = []
            awards = userData["awards"]
            Rank = userData["rank"]
            Status = ""
            Links = []

            for key, value in list(awards.items()):
                if str(value) == 0:
                    Value = "Badge"
                elif str(value) == 1:
                    Value = "Standard"
                elif str(value) == 2:
                    Value = "Bronze"
                elif str(value) == 3:
                    Value = "Silver"
                elif str(value) == 4:
                    Value = "Gold"
                elif str(value) == 5:
                    Value = "Diamond"
                Awards.append("{0}: {1}".format(key, Value))

            for key, value in userData["links"]:
                Links.append("{0}: {1}".format(key, value))
            Links = ", ".join(Links)
            Awards = ", ".join(Awards)

            if userData["voucher"]:
                Status = "This member has a voucher"
                if userData["safe"] == 1:
                    Status += " and is safe for the next IMC/IRC"
                elif userData["safe"] == 2:
                    Status += " and is autosafe";
            else:
                if userData["safe"] == 1:
                    Status += "This member is safe for the next IMC/IRC"
                elif userData["safe"] == 2:
                    Status += "This member is absolutely necessary to keep the group going and thus is autosafe"
	
            irc.reply("Member is: {0} {1} | {2} | http://brilliant-minds.tk/members.html?{3} | Awards {4} | {5}".format(Rank, userName, Safe, userName, Awards, Links), prefixNick=False)
            self.log.info("UserInfo: Member {0} found".format(userName))
        except Exception:
            irc.reply("User {0} doesn't have any record in my database, sorry.".format(userName))
            self.log.error("UserInfo: Member {0} not found".format(userName))
        finally:
            return None

Class = UserInfo

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
