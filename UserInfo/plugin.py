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
import json,random,urllib,re
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
		# self._getMemberInfo(irc, user, 0)
	# profile = wrap(profile,['somethingWithoutSpaces',optional('text')])

	# def _getMemberInfo(self, irc, user):
		# """<username>

		# returns a link to a user's profile and some information"""
		try:
			if not user.startswith("http://"):
				userPage = utils.web.getUrl("http://brilliant-minds.tk/members.html?{0}".format(user))
				userName = user
			else:
				if user.startswith("https://"):
					user = "http" + user.split("https")[0]
				userPage = utils.web.getUrl(user)
				userName = user.split("http://brilliant-minds.tk/members.html?")[0]

			userData = json.loads(utils.web.getUrl("http://brilliant-minds.tk/members/{0}.json".format(userName)))
			Awards = []
			Rank = userData["rank"]
			Status = ""
			Links = []
			if userData["awards"]:
				for key, value in jsonObject["awards"].items():
					Awards.append("{name}: {value}".format(name=key, value=str(value)))
			if userData["links"]:
				for key, value in jsonObject["links"]:
					Links.append("{name}: {link}".format(name=key, value=link))
			Links = ", ".join(Links)
			Awards = ", ".join(Awards)
			if userData["voucher"]:
				Status += "This member has a voucher"
				if userData["safe"] == 1:
					Status += " and is safe for the next IMC/IRC"
				elif userData["safe"] == 2:
					Status += " and is autosafe";
			else:
				if userData["safe"] == 1:
					Status += "This member is safe for the next IMC/IRC";
				elif userData["safe"] == 2:
					Status += "This member is absolutely necessary to keep the group going and thus is autosafe"
			if self.registryValue("MemberSnarfer") == False:
				return
			else:
				irc.reply("{0} {1} | {2} | http://brilliant-minds.tk/members.html?"+userName+" | Awards {3} | {4}".format(Rank,userName,Safe,Awards,Links))
		# except Exception:
			# try:
				# userPage = utils.web.getUrl("http://brilliant-minds.tk/members.html?"+user)
				# userName = userPage.split("<h4>")[1].split("</h4>")[0]
				# userData = json.loads(utils.web.getUrl("http://brilliant-minds.tk/members/"+user+".json"))
				# Awards = userData["awards"]
				# Rank = userData["rank"]
				# if self.registryValue("MemberSnarfer") == False:
					# return
				# else:
					# irc.reply("{0} {1} http://brilliant-minds.tk/members.html?{0} | Awards {2}".format(Rank,user,Awards))
		except Exception, e:
			irc.reply("User {0} doesn't have any record in my database, sorry.".format(user))
		finally:
			return None
	userSnarfer = wrap(profile,["something"])

Class = UserInfo

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
