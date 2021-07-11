# WILSON Cloud Respwnder

[![Twitter Follow](https://img.shields.io/twitter/follow/honoki?style=flat-square)](https://twitter.com/honoki)

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
* A full NGINX server is at your disposal for advanced configuration options;
* A full bind9 DNS server allows you to host arbitrary DNS records for advanced test cases;

## Limitations

* No support for protocols other than HTTP and DNS;
* Due to limitations of Slack and Discord notifications, HTTP requests are truncated if the request body is larger than ~2KB or ~3KB respectively. Full HTTP messages can be viewed in `/logs/mitm/http.log` when that happens;


## Installation

WILSON Cloud Respwnder requires you to have a registered domain `yourdomain.com` with its nameserver(s) pointing to the server where you're installing this.

1. Clone this repository: `git clone https://github.com/honoki/wilson-cloud-respwnder`;
2. Run `./setup.sh yourdomain.com` to generate the required config files;
3. Step through the required steps to generate your Letsencrypt certificate;
4. Edit `settings.env` to include your Slack and/or Discord webhooks;
5. Run `sudo docker-compose up`

## Acknowledgments

Thanks to [@michenriksen](https://twitter.com/michenriksen) for suggesting the name Wilson, referencing the [Wilson cloud chamber](https://en.wikipedia.org/wiki/Cloud_chamber) used to visualize the passage of ionizing radiation.