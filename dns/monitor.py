#!/usr/bin/python3
import time, requests, os
from multiprocessing.dummy import Pool

def is_blacklisted(domain):
    blacklist  = open("/data/blacklist.txt")
    return domain in [w.strip() for w in blacklist.readlines()]

def escape_domain(domain):
    return domain.replace(os.environ.get('DOMAIN'), '[.]'.join(os.environ.get('DOMAIN').rsplit('.', 1)))

def watch(fn):
    try:
        fp = open(fn, 'r')
        fp.seek(0,2) # start at the end
        while True:
            new = fp.readline()

            if new:
                parts = new.split(' ')
                yield (parts[7].lower(), parts[9], parts[4])
            else:
                time.sleep(0.5)
    except Exception as e:
        print("Error occurred while monitoring queries.log:",e)

queries = '/var/log/named/queries.log'

# Send a message to say we're up and running
message = "[WILSON] DNS server deployed and listening on `*."+os.environ.get('DOMAIN')+"`"
requests.post( os.environ.get('DISCORD_WEBHOOK'), json = { 'content': message } ) if os.environ.get('DISCORD_WEBHOOK') else False
requests.post( os.environ.get('SLACK_WEBHOOK'), json = {'text': message} ) if os.environ.get('SLACK_WEBHOOK') else False

# wrap a while loop around this to retry after an error occurred in watch(queries)
while True:
    for domain, type, fromip in watch(queries):
        print(domain, type, fromip)
        if os.environ.get('DOMAIN') not in domain or domain == os.environ.get('DOMAIN'):
            print("illegal request")
        elif is_blacklisted(domain):
            print("skipping blacklisted domain", domain)
        else:
            message = '[dns] ['+type+'] '+escape_domain(domain)+ ' from '+fromip
            # make an asynchronous request to the webhooks so the responsiveness of the logging isn't impacted
            pool = Pool()
            pool.apply_async(requests.post, ( os.environ.get('DISCORD_WEBHOOK'), ), { 'json': { 'content': message } } )
            pool.apply_async(requests.post, ( os.environ.get('SLACK_WEBHOOK'), ), { 'json': {'text': message} })
