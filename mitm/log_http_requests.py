#!/usr/bin/python3
import os, requests
from multiprocessing.dummy import Pool
from ipwhois import IPWhois

def is_blacklisted(domain):
    blacklist  = open("/data/blacklist.txt")
    return domain in [w.strip() for w in blacklist.readlines()]

def escape_domain(domain):
    return domain.replace(os.environ.get('DOMAIN'), '[.]'.join(os.environ.get('DOMAIN').rsplit('.', 1)))

def request(flow):
    req = flow.request.method + ' ' + flow.request.path + ' ' + flow.request.http_version + '\n'

    host = None
    fromip = None
    proto = 'http'

    for k, v in flow.request.headers.items():
        if k == 'X-MITMProxy-Real-IP':
            fromip = v
            continue
        if k == 'X-MITMProxy-Real-Proto':
            proto = v
            continue
        if k.lower() == 'host' and v == 'localhost':
            continue
        # don't send our internal hostnames to Slack yo
        if k.lower() == 'host' and v == 'nginx-server:8000':
            continue
        # and put the proxied X-MITMProxy-Host back where it belongs
        if k == 'X-MITMProxy-Host':
            host = v
            if is_blacklisted(v):
                return
            if os.environ.get('DOMAIN') not in host:
                return
            req = req + ("Host: %s" % v)+'\n'
            continue
        req = req + ("%s: %s" % (k, v))+'\n'
    req = req + '\n'+flow.request.content.decode("utf-8")
    
    # replace http: by hxxp: to avoid Slack resolving the URL when the notification is sent
    req = req.replace('http:', 'hxxp:')
    req = req.replace('https:', 'hxxps:')

    # get the origin country
    from_country = IPWhois(fromip).lookup_whois()['asn_country_code'].lower()
    
    slack_msg = {
        "text": "["+proto+"] "+host+flow.request.path,
        "blocks":[
            {"type":"section","text":{"type":"mrkdwn","text":"["+proto+"] request from `"+fromip+"` :flag-"+from_country+": to `"+escape_domain(host)+flow.request.path+"`"}},
            {"type":"section","text":{"type":"mrkdwn","text":"```"+req[:2500]+("[...]" if len(req) > 2500 else "") + "```"}}
        ]
    }

    discord_msg = {
        "content": "["+proto+"] request from `"+fromip+"` :flag-"+from_country+": to `"+escape_domain(host)+flow.request.path+"`",
        "embeds": [{
            "description": "```"+req[:3500]+("[...]" if len(req) > 3500 else "")+"```"
        }]
    }

    # make an asynchronous request to the webhook so the responsiveness of the server isn't impacted
    pool = Pool()
    pool.apply_async(requests.post, ( os.environ.get('SLACK_WEBHOOK'), ), { 'json': slack_msg })
    pool.apply_async(requests.post, ( os.environ.get('DISCORD_WEBHOOK'), ), { 'json': discord_msg } )

    # write the request to http.log
    with open("/http.log", "a") as logfile:
        logfile.write(req)
