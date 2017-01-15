###
# Copyright (c) 2017, fluxkompensator
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
import supybot.schedule as sched
import supybot.ircmsgs as ircmsgs
import datetime
import time
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Voicer')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class Voicer(callbacks.Plugin):
    """Voices people when they talk and removes voice after period of time."""
    threaded = True
    nicks = {}
    #irc.queueMsg(ircmsgs.privmsg('#Mail', 'nick'))
    #irc.noReply()
    """Auto voices and devoices users when they idle or start talking"""

    def deVoice(self, irc, channel, nick, schedname):
        irc.queueMsg(ircmsgs.devoice(channel, nick))
        irc.noReply()
        self.nicks.pop(schedname)
        return 0
        
    def doPrivmsg(self, irc, msg):
        if self.registryValue('Duration'):
            self.delay = self.registryValue('Duration')
        else:
            self.delay = 600 
        if ircmsgs.isCtcp(msg) and not ircmsgs.isAction(msg):
            return
        if irc.isChannel(msg.args[0]):
            channel = msg.args[0]
            said = ircmsgs.prettyPrint(msg)
            nick = msg.nick
            schedname = str(channel.strip('#'))+str(nick)
            voices = irc.state.channels[channel].voices
            if nick not in voices:
                irc.queueMsg(ircmsgs.voice(channel, nick))
                irc.noReply()
            if schedname not in self.nicks:
                sched.addEvent(self.deVoice, time.time()+self.delay, schedname, (irc,channel,nick,schedname))
            else:
                #self.sched.rescheduleEvent(schedname, time.time()+10) # does not work because the arguments get lost in this function
                sched.removeEvent(schedname)
                sched.addEvent(self.deVoice, time.time()+self.delay, schedname, (irc,channel,nick,schedname))
            self.nicks[schedname] = datetime.datetime.now()
    #voice = wrap()
Class = Voicer


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
