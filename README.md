# WILSON Cloud Respwnder

[![Bluesky Follow](https://img.shields.io/badge/Bluesky-@honoki.net-blue?style=flat-square&logo=bluesky)](https://bsky.app/profile/honoki.net)

## What is this?

WILSON Cloud Respwnder is a Web Interaction Logger Sending Out Notifications (WILSON) with the ability to serve custom content in order to appropriately respond to the client issuing the request. It is probably most useful to security testers and bug bounty hunters.

When exploiting bugs that interact with an external server (e.g. SSRF or some XSS), it is sometimes useful to serve custom content on specific paths on the remote server. With WILSON Cloud Respwnder you can setup a fully functional PHP web server with transparent logging of all incoming DNS and HTTP requests to a Slack or Discord channel.

## Features

* Monitor DNS and HTTP requests in real-time without time window constraints. Continue receiving notifications for weeks or months on end to find more bugs;
* Send notifications to Slack and/or Discord webhooks;
* View the complete HTTP requests in your logs, including POST bodies;
* By default resolves every `subdomain.yourdomain.com` to the same web server, allowing you to choose meaningful names that are easy to work with;
* Filter out specific domains from cluttering your notifications by adding them to `/data/blacklist.txt`;
* Modify and serve your own content on the PHP web server by writing files to `/www`;
* A full Caddy server with automatic TLS certificate management is at your disposal for advanced configuration options;
* A full bind9 DNS server allows you to host arbitrary DNS records for advanced test cases;

## Installation

WILSON Cloud Respwnder requires you to have a registered domain `yourdomain.com` with its nameserver(s) pointing to the server where you're installing this.

1. Clone this repository: `git clone https://github.com/honoki/wilson-cloud-respwnder`;
2. Run `./setup.sh yourdomain.com` to generate the required config files;
3. Edit `settings.env` to include your Slack and/or Discord webhooks;
4. Run `sudo docker compose up -d --build`
5. Test if things are working by browsing to `https://random-subdomain.yourdomain.com/randompage`

TLS certificates for `yourdomain.com` and `*.yourdomain.com` are obtained automatically from Let's Encrypt via DNS-01 challenge on first startup. No manual certificate management is required.

## Limitations

* No support for protocols other than HTTP and DNS;
* Due to limitations of Slack and Discord notifications, HTTP requests are truncated if the request body is larger than ~2KB or ~3KB respectively. Full HTTP messages can be viewed in `/logs/mitm/http.log` when that happens;
* Nested subdomains (e.g. `test.sub.yourdomain.com`) will resolve to your server, but are not covered by the wildcard certificate (`*.yourdomain.com` only covers one level deep). HTTP requests will work as expected, but HTTPS requests may fail.

## Acknowledgments

Thanks to [@michenriksen](https://twitter.com/michenriksen) for suggesting the name Wilson, referencing the [Wilson cloud chamber](https://en.wikipedia.org/wiki/Cloud_chamber) used to visualize the passage of ionizing radiation.
