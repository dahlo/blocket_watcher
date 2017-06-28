#!/usr/bin/env python

from ConfigParser import SafeConfigParser
import os
import sys
import json
import urllib
# from IPython.core.debugger import Tracer
from datetime import datetime
import requests

from email.mime.text import MIMEText
from subprocess import Popen, PIPE


try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup




def alert_user(new_ads, config, url):

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
		
	# send the email
	emails = config.get('settings', 'email').split(",")
	requests.post(
        "https://api.mailgun.net/v3/{}/messages".format(config.get('settings', 'mailgun_domain')),
        auth=("api", config.get('settings', 'mailgun_key')),
        data={"from": "Blocket Watcher <blocket.watcher@{}>".format(config.get('settings', 'mailgun_domain')),
              "to": emails,
              "subject": "Blocket Watcher: {} new ad{} for '{}'".format(len(new_ads), multiple, search_string),
              "text": msg})






# get working dir
workdir = os.path.dirname(os.path.realpath(__file__))


# read the config file
config = SafeConfigParser()
config.read('{}/watcher.conf'.format(workdir))



# get the url to watch
usage = 'python {} "<url to watch>"'.format(sys.argv[0])
try:
	url = sys.argv[1]
except:
	sys.exit(usage)


# try to open the history file
try:
	with open("{}/history.json".format(workdir), 'r') as history_file:
		history = json.load(history_file)
except:
	print("Failed to open history file {}, creating a new one.".format("history.json"))
	history = {url:{'date':'1970-01-01 00:00:00'}}



# open the url to watch
resp = urllib.urlopen(url) 
html = resp.read()   
page = BeautifulSoup(html, "lxml")

# create date to compare to
last_update = datetime.strptime(history[url]['date'], '%Y-%m-%d %H:%M:%S')

# init
new_ads = []

# find all ads
for ad in page.findAll('article', 'media'):

	# get ad date
	ad_date = datetime.strptime(ad.div.header.time['datetime'], '%Y-%m-%d %H:%M:%S')

	# check if it's a new ad
	if ad_date > last_update:

		# the ad is new and should be reported to the user
		new_ads.append(ad)



# if there are any new ads to report
if new_ads:
	alert_user(new_ads, config, url)



# update the history
history[url]['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# save the history file again
with open("{}/history.json".format(workdir), "w") as history_file:
	json.dump(history, history_file)