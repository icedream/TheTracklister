#!/usr/bin/env python
import logging

import threading

from bot.twitter import TwitterBot
from bot.irc import IrcBot

Configuration = {}

def main():
	# prepare logging
	logging.basicConfig(level=logging.INFO)

	# load configuration
	exec(open("tracklister.conf").read(), Configuration)
	
	# load irc bot
	irc = IrcBot(Configuration)
	t = threading.Thread(target=irc.start)
	t.daemon = True
	t.start()

	# load twitter bot
	twitter = TwitterBot(Configuration, irc)
	twitter.start()

if __name__ == "__main__":
	main();