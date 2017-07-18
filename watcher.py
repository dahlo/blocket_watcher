#!/usr/bin/env python

from ConfigParser import SafeConfigParser
import os
import sys
import json
import urllib
# from IPython.core.debugger import Tracer
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests

from email.mime.text import MIMEText
from subprocess import Popen, PIPE



from bs4 import BeautifulSoup





def alert_user(new_ads, config, url):

	# print "alert"

	# pluralize
	multiple = ""
	if len(new_ads) > 1:
		multiple = "s"
	

	# get the search string
	search_string = url.split('q=')[1].split('&')[0].replace('+',' ')

	

	# send an email to 
	msg = u"""Hello there
There are {} new ad{} for the Blocket search '{}', {}


""".format(len(new_ads), multiple, search_string, url)

	for ad in new_ads:

		# get ad info
		price = ad.div.p.text
		if not price:
			price = "No price"

		title = ad.div.h1.a['title']
		link = ad.div.h1.a['href']
		
		msg += u"""{}
{}
{}

""".format(title, price, link)

	# add friendly signature
	msg += "\nCheers\nThe Blocket Watcher"
	subject = "Blocket Watcher: {} new ad{} for '{}'".format(len(new_ads), multiple, search_string)
		
	# send the email
	emails = config.get('settings', 'email').split(",")
	requests.post(
        "https://api.mailgun.net/v3/{}/messages".format(config.get('settings', 'mailgun_domain')),
        auth=("api", config.get('settings', 'mailgun_key')),
        data={"from": "Blocket Watcher <blocket.watcher@{}>".format(config.get('settings', 'mailgun_domain')),
              "to": emails,
              "subject": subject,
              "text": msg})



	# if there is a pushbullet api key given
	if config.get("settings", "pushbullet_key"):

		# send a pushbullet
		from pushbullet import Pushbullet
		pb = Pushbullet(config.get("settings", "pushbullet_key"))
		pb.push_note(subject, msg)








# get working dir
workdir = os.path.dirname(os.path.realpath(__file__))


# get the url to watch
usage = 'python {} <config file> "<url to watch>"'.format(sys.argv[0])
try:
	config_file = sys.argv[1]
	url = sys.argv[2]
except:
	sys.exit(usage)


# read the config file
config = SafeConfigParser()
config.read('{}/{}'.format(workdir, config_file))

# Tracer()()

# try to open the history file
try:
	with open("{}/history.{}.json".format(workdir, ".".join(config_file.split('.')[:-1])), 'r') as history_file:
		history = json.load(history_file)
except:
	print("Failed to open history file {}, creating a new one.".format("history.json"))
	history = {url:{'ads':[]}}



# open the url to watch
resp = urllib.urlopen(url) 
html = resp.read()   
page = BeautifulSoup(html, "lxml")

# create date to compare to
try:
	historic_ads = history[url]['ads']
except:
	history[url] = {'ads':[]}
	historic_ads = history[url]['ads']

# init
new_ads = []
current_ads = []

# find all ads
for ad in page.findAll('article', 'media'):

	# Tracer()()

	# save the id as seen
	current_ads.append(ad['id'])

	# check if the url has been seen before
	if ad['id'] not in historic_ads:

		# check if the ad is old enough, and not just an old ad that was on page 2 of the results, but reached page 1 because a newer ad was removed
		if datetime.strptime(ad.div.header.time['datetime'], '%Y-%m-%d %H:%M:%S') > (datetime.now() - relativedelta(hours=24)):

			# save the ad as a new ad
			new_ads.append(ad)


# Tracer()()
# if there are any new ads to report
if new_ads:
	alert_user(new_ads, config, url)



# update the history
history[url]['ads'] = current_ads

# save the history file again
with open("{}/history.{}.json".format(workdir, ".".join(config_file.split('.')[:-1])), "w") as history_file:
	json.dump(history, history_file)