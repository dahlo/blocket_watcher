# blocket_watcher
Watches blocket for new ads and alerts when there is something new.

# Requirements
Uses Mailgun.org to send emails. Get a domain and account there. Or rewrite the email sending to use gmail or whatever service you want.

# Installation
Rename watcher.conf.dist to watcher.conf and modify the file with your settings.

# Usage
Add one instance per url you want to watch to your crontab, maybe run it every 10 min or so. Try not to run multiple instances at the same time, as they will probably overwrite the `history.db` file and mess stuff up for each other.

python blocket_watcher.py "<url to watch>"

Ex.

```bash
$ python blocket_watcher.py "https://www.blocket.se/uppsala?q=skor&cg=0&w=1&st=s&c=&ca=10&is=1&l=0&md=th"
```
