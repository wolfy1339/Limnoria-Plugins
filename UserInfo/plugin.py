###
# Copyright (c) 2014, wolfy1339
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
import json,random,urllib,re
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('UserInfo')
except ImportError:
    _ = lambda x:x

class UserInfo(callbacks.Plugin):
    """A plugin that fetches member information from the website"""
    threaded = True
	def browse(self, irc, msg, args, ID, blurb):
		"""<memberName>
		Returns user information from their record"""
		self._getMemberInfo(irc, ID, 0)
	browse = wrap(browse,['somethingWithoutSpaces',optional('text')])
	def userSnarfer(self, irc, ID, urlGiven):
		"""<username>
		returns a link to a users profile and some information"""
		try:
			userPage = utils.web.getUrl("http://brilliant-minds.tk/members.html?"+user)
			userName = userPage.split("<h4>")[1].split("</h4>")[0]
			userData = json.loads(utils.web.getUrl("http://brilliant-minds.tk/members/"+user+".json"))
			uDu = userData['User']
			irc.reply("http://brilliant-minds.tk/members.html?{1} | Awards {3})
			except Exception, e:
				try"
					userPage = utils.web.getUrl("http://brilliant-minds.tk/members.html?"+user)
				userName = userPage.split("<h4>")[1].split("</h4>")[0]
				userData = json.loads(utils.web.getUrl("http://brilliant-minds.tk/members/"+user+".json"))
				uDu = userData['User']
				irc.reply("http://brilliant-minds.tk/members.html?{1} | Awards {3})
				except Exception, e:
					irc.reply("User doesn't have any record in my database, sorry. {}".format(e))\
			finally:
				return None
		userSnarfer = wrap(profile,['something']

Class = UserInfo

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
