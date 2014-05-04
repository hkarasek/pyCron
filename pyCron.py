#               ___
#              (  _`\
# _ _    _   _ | ( (_) _ __   _     ___
#( '_`\ ( ) ( )| |  _ ( '__)/'_`\ /' _ `\
#| (_) )| (_) || (_( )| |  ( (_) )| ( ) |
#| ,__/'`\__, |(____/'(_)  `\___/'(_) (_)
#| |    ( )_| |
#(_)    `\___/'
#
#	build: 	1|3/5/2014
#	author: Jan Karásek
#

from time import sleep, time
from datetime import datetime
from pprint import pprint
import signal
import sys

from requests import get


CONFIG_FILE = 'cron.conf'
LOG_FILE = 'cron.log'
LOG_SUCCES = False
DEFAULT_TIMEOUT = 15 # seconds


def loadConf():
	global DEFAULT_TIMEOUT
	CONF = []
	with open(CONFIG_FILE, 'r') as file:
		for line in file:
			if line[0] == '#':
				continue
			line = line.split('[]')
			try:
				line[2] = int(line[2])
			except:
				line.append(DEFAULT_TIMEOUT)
			line[1] = int(line[1])
			line.append(0)
			CONF.append(line)
	return CONF


def exit_gracefully(signum, frame):
	# restore the original signal handler as otherwise evil things will happen
	# in input when CTRL+C is pressed, and our signal handler is not re-entrant
	signal.signal(signal.SIGINT, original_sigint)

	try:
		if input("\nReally quit? (y/n)> ").lower().startswith('y'):
			sys.exit(1)

	except KeyboardInterrupt:
		print("Ok ok, quitting")
		sys.exit(1)

	# restore the exit gracefully handler here
	signal.signal(signal.SIGINT, exit_gracefully)


class Log:
	def __init__(self, logFile, logAll=False):
		self.f = open(logFile, 'a')
		self.logAll = logAll

	def error(self, link):
		logMes = '(' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ')\tdown\t\t' + str(link) + '\n'
		print(logMes, end='')
		self.f.write(logMes)
		self.f.flush()

	def info(self, link):
		logMes = '(' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ')\tsuccess\t\t' + str(link) + '\n'
		print(logMes, end='')
		if self.logAll:
			self.f.write(logMes)
			self.f.flush()

	def __del__(self):
		self.f.close()


CONF = loadConf()
pprint(CONF)
log = Log(LOG_FILE, logAll=False)

original_sigint = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, exit_gracefully)

while 1:
	for link in CONF:
		if link[-1] + link[1] < time():
			try:
				r = get(link[0], timeout=link[2])
				if r:
					log.info(link[0])
					link[-1] = time()
			except:
				log.error(link[0])
				link[-1] = time()
	sleep(0.2)
