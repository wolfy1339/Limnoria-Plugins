###
# Copyright (c) 2011, Anthony Boot
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import supybot.schedule as schedule
import random
import time


class CustOps(callbacks.Plugin):
    """Custom op commands."""

    threaded = True

    random.seed()
    for each in range(0, random.randint(50, 100)):
        i = random.random()
    del i

    @wrap(['op', ('haveOp', 'remove a user from the channel'), 'nickInChannel', additional('text')])
    def ninja(self, irc, msg, args, channel, user, reason):
        """<user> [reason]

        Forces a user to part the channel.
        Essentially a kick without the counter."""

        if not reason:
            reason = '{0} says GTFO.'.format(msg.nick)

        irc.queueMsg(ircmsgs.IrcMsg('REMOVE {0} {1} :{2}'.format(channel, user,
                                                                 reason)))

    @wrap(['op', ('haveOp', 'Evict a user to #powder-social'), 'nickInChannel', optional('anything')])
    def social(self, irc, msg, args, channel, user, junk):
        """[#powder] <user>

        Sets a redirection ban from #powder to #powder-social,
        kicks the user (exploiting a users auto-rejoin
        to force them to #powder-social) then lifts the ban.
        Also sends the user a notice informing them of what happened."""

        if channel not in '#powder':
            channel = '#powder'
        hostmask = irc.state.nickToHostmask(user)
        irc.queueMsg(ircmsgs.IrcMsg(
            'MODE #powder +b {0}$#powder-social'.format(hostmask)))
        irc.queueMsg(ircmsgs.IrcMsg(
            'KICK #powder {0} :Take it to #powder-social'.format(user)))
        irc.queueMsg(ircmsgs.invite(user, '#powder-social'))
        irc.queueMsg(ircmsgs.IrcMsg((
            'NOTICE {0} :{1} has requested you take your current conversation',
            'to #powder-social.').format(
                    user, msg.nick)))
        expires = time.time() + 300

        def f():
            irc.queueMsg(ircmsgs.IrcMsg(
                'MODE #powder -b {0}$#powder-social'.format(hostmask)))

        schedule.addEvent(f, expires)

    @wrap(['op', ('haveOp', 'Quiet a user'), 'nickInChannel', optional('int'), optional('text')])
    def stab(self, irc, msg, args, channel, user, timer, reason):
        """<user> [seconds] [reason (ignored)]

        Stabs a user, putting them on quiet for a random time up to 10 mins."""

        hmask = irc.state.nickToHostmask(user)
        hostmask = ircutils.joinHostmask(
            '*', '*', ircutils.hostFromHostmask(hmask))
        irc.queueMsg(ircmsgs.IrcMsg(
            'MODE {0} +q {1}'.format(channel, hostmask)))

        t = time.time()
        r = timer or 0
        if not r > 0:
            r = random.randint(30, 600)
        expires = t + r

        len = {}
        len['m'] = len['s'] = 0

        while r > 59:
            len['m'] += 1
            r -= 60

        len['s'] = r

        irc.queueMsg(ircmsgs.IrcMsg(
            'NOTICE +{0} :{1} has been quieted for {2}:{3:0>2}'.format(
                    channel, user,  len['m'], len['s'])))

        def f():
            irc.queueMsg(ircmsgs.IrcMsg(
                'MODE {0} -q {1}'.format(channel, hostmask)))

        schedule.addEvent(f, expires)
        irc.noReply()

    @wrap(['op', ('haveOp', 'Unquiet a user'), 'nickInChannel', optional('int'), optional('text')])
    def unstab(self, irc, msg, args, channel, user):
        """<user>

        Removes +q from a user in channel"""

        hmask = irc.state.nickToHostmask(user)
        hostmask = ircutils.joinHostmask(
            '*', '*', ircutils.hostFromHostmask(hmask))
        irc.queueMsg(ircmsgs.IrcMsg(
            'MODE {0} -q {1}'.format(channel, hostmask)))

Class = CustOps

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
