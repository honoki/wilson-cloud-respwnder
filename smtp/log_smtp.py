#!/usr/bin/env python3
import asyncio, os, email, email.policy, requests, datetime
from aiosmtpd.controller import Controller
from ipwhois import IPWhois

DOMAIN = os.environ.get('DOMAIN', '')
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK')


def escape_domain(s):
    return s.replace(DOMAIN, '[.]'.join(DOMAIN.rsplit('.', 1)))


def get_country(ip):
    try:
        return IPWhois(ip).lookup_whois()['asn_country_code'].lower()
    except Exception:
        return None


def extract_body(msg):
    if msg.is_multipart():
        parts = []
        for part in msg.walk():
            if part.get_content_type() in ('text/plain', 'text/html'):
                try:
                    parts.append(part.get_payload(decode=True).decode('utf-8', errors='replace'))
                except Exception:
                    pass
        return '\n---\n'.join(parts)
    try:
        return msg.get_payload(decode=True).decode('utf-8', errors='replace')
    except Exception:
        return str(msg.get_payload())


# startup notification
_startup = f"[WILSON] SMTP server deployed and listening on `*@*.{DOMAIN}` (port 25)"
if DISCORD_WEBHOOK:
    requests.post(DISCORD_WEBHOOK, json={'content': _startup})
if SLACK_WEBHOOK:
    requests.post(SLACK_WEBHOOK, json={'text': _startup})


class EmailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        peer_ip = session.peer[0]
        mail_from = envelope.mail_from
        rcpt_tos = envelope.rcpt_tos
        raw = envelope.content.decode('utf-8', errors='replace')

        msg = email.message_from_string(raw)
        subject = msg.get('Subject', '(no subject)')
        recipients = ', '.join(rcpt_tos)

        country = get_country(peer_ip)
        flag = f":flag-{country}:" if country else ""

        timestamp = datetime.datetime.utcnow().isoformat()
        log_entry = (
            f"[{timestamp}] FROM:{mail_from} TO:{recipients} IP:{peer_ip}\n"
            f"{raw[:10000]}\n"
            f"{'='*60}\n"
        )

        # defang URLs
        display_raw = raw.replace('http:', 'hxxp:').replace('https:', 'hxxps:')
        truncated = display_raw[:2500] + ("[...]" if len(display_raw) > 2500 else "")

        if SLACK_WEBHOOK:
            try:
                requests.post(SLACK_WEBHOOK, json={
                    "text": f"[smtp] {mail_from} → {recipients}",
                    "blocks": [
                        {"type": "section", "text": {"type": "mrkdwn",
                            "text": f"[smtp] email from `{mail_from}` (`{peer_ip}` {flag}) to `{escape_domain(recipients)}`\nSubject: *{subject}*"}},
                        {"type": "section", "text": {"type": "mrkdwn",
                            "text": "```" + truncated + "```"}}
                    ]
                })
            except Exception:
                pass

        if DISCORD_WEBHOOK:
            try:
                requests.post(DISCORD_WEBHOOK, json={
                    "content": f"[smtp] email from `{mail_from}` (`{peer_ip}` {flag.replace('-', '_')}) to `{escape_domain(recipients)}`\nSubject: **{subject}**",
                    "embeds": [{"description": "```" + display_raw[:3500] + ("[...]" if len(display_raw) > 3500 else "") + "```"}]
                })
            except Exception:
                pass

        with open(os.environ.get('SMTP_LOG', '/smtp.log'), 'a') as f:
            f.write(log_entry)

        return '250 Message accepted for delivery'


if __name__ == '__main__':
    port = int(os.environ.get('SMTP_PORT', 25))
    controller = Controller(EmailHandler(), hostname='0.0.0.0', port=port)
    controller.start()
    print(f"[WILSON] SMTP server listening on port {port} for *@*.{DOMAIN}")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()
