# blocket_watcher
Watches blocket for new ads and alerts when there is something new.

# Requirements
Uses Mailgun.org to send emails. Get a domain and account there. Or rewrite the email sending to use gmail or whatever service you want.

Requires a couple of python modules as well:

```bash
$ pip install bs4 python-dateutil

# if pushbullet support is needed
$ pip install pushbullet.py
```

# Installation
Rename watcher.conf.dist to watcher.conf and modify the file with your settings.

# Usage
Add one instance per url you want to watch to your crontab, maybe run them every 10 min or so. If different people are interesten in different urls, use different config files for each url with the correct people in each file.

```bash
python blocket_watcher.py <config file to use> "<url to watch>"
```

Ex.

```bash
$ python blocket_watcher.py watcher.conf "https://www.blocket.se/uppsala?q=skor&cg=0&w=1&st=s&c=&ca=10&is=1&l=0&md=th"
```
