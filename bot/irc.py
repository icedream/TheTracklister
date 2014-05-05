import string
import time
import logging
import os

try:
	import requests
except:
	print("Failed at loading the requests library. Did you forget to install the package \"requests\"?")
	sys.exit(-1)
	
try:
	import irc.bot
	import irc.client
	import irc.strings
except:
	print("Failed at loading the IRC library. Did you forget to install the package \"irc\"?")
	sys.exit(-1)

IRC_COLOR="\x03"
IRC_BOLD="\x02"
IRC_RESET="\x0f"

# Handles IRC events/messages
class IrcBot(irc.bot.SingleServerIRCBot):
	config = None
	server = None
	port = 6667
	nickname = None
	username = None
	realname = None
	nickservpass = None
	channel = None
	owner = None
	logger = None
	
	current_dj = ""

	def __init__(self, config):
		self.logger = logging.getLogger(__name__)
		
		self.config = config
		
		self.server = config["IRC"]["Host"] if "Host" in config["IRC"] else "irc.mixxnet.net"
		self.port = int(config["IRC"]["Port"] if "Port" in config["IRC"] else "6667")
		self.nickname = config["IRC"]["Nickname"] if "Nickname" in config["IRC"] else "TheTracklister"
		self.username = config["IRC"]["Username"] if "Username" in config["IRC"] else "tracklist"
		self.realname = config["IRC"]["Realname"] if "Realname" in config["IRC"] else "The Tracklister bot"
		self.nickservpass = config["IRC"]["NickServPassword"] if "NickServPassword" in config["IRC"] else None
		self.triggers = {}
		
		self.logger.info("Initializing IRC bot (%s:%d)", self.server, self.port)
		irc.bot.SingleServerIRCBot.__init__(self, [(self.server, self.port)], self.nickname, self.realname, 60, username=self.username)
	
	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")
		
	# Does nickserv authentication
	def do_nickserv_auth(self):
		if self.nickservpass is not None:
			self.logger.info("NickServ authentication running...")
			self.connection.privmsg("NickServ", "IDENTIFY {}".format(self.nickservpass))
			self.connection.privmsg("HostServ", "ON")

	# Initial startup for when the bot has finished connecting to IRC.
	def on_welcome(self, c, e):
		self.logger.info("Connected to IRC server.")
		self.do_nickserv_auth()
		
		# join all channels
		cs = ",".join(self.get_all_channels())
		self.logger.info("Joining all channels: %s" % cs)
		c.join(cs)
	
	# triggers when we receive a public (channel) IRC message
	def on_pubmsg(self, c, e):
		msg = e.arguments[0]
		
		nick = e.source.nick
		channel = e.target
		parts = msg.split(' ')
		trigger = parts[0]
		data = parts[1:]
		self.logger.info('[%s] <%s> %s', channel, nick, msg)

		trigger_func = self.triggers.get(trigger, self.trigger_default)
		trigger_func(nick, channel, data)
	
	# triggers when we receive a private IRC message
	def on_privmsg(self, c, e):
		msg = e.arguments[0]
		
		self.logger.info('[%s] <%s> %s', "private", e.source.nick, msg)

	# gets all channels related to this bot by configuration
	def get_all_channels(self):
		channels = []
		for show_name in self.config["Shows"].keys():
			for channel in self.config["Shows"][show_name]["IrcChannels"]:
				if not channel in channels: # avoid duplicates
					channels.append(channel)
		return channels

	# broadcast any message
	def broadcast(self, text):
		self.connection.privmsg(self.channel, text)
		
	#######################
	# IRC command triggers
	
	def install_trigger(name, func):
		self.triggers[name] = func;
		
	# we got a command but it doesn't match any of the triggers
	def trigger_default(self, nick, channel, data):
		# *snore*
		return
