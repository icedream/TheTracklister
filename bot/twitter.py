import sys
import logging
import time

try:
	from TwitterAPI import TwitterAPI
except:
	print("Failed at loading the Twitter API. Did you forget to install the package \"TwitterAPI\"?")
	sys.exit(-1)

class TwitterBot():
	def __init__(self, config, irc):
		self._log = logging.getLogger(__name__)
		
		self._config = config
		self._api = TwitterAPI(
				config["Twitter"]["ApiKey"],
				config["Twitter"]["ApiSecret"],
				config["Twitter"]["AccessToken"],
				config["Twitter"]["AccessTokenSecret"])
		self._irc = irc
				
	def start(self):
		r = self._api.request("statuses/filter", {"track":"#nowplaying"})
		for item in r.get_iterator():
			self._log.info(item["text"] if "text" in item else "<no text in this tweet>")
			#time.sleep(1)