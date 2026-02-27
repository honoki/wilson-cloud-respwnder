(acme_dns) {
    tls {
        dns rfc2136 {
            key_name acme-key
            key_alg  hmac-sha256
            key      {env.TSIG_SECRET}
            server   dns:53
        }
    }
}

(mitm_proxy) {
    header -Server
    reverse_proxy mitmproxy:30001 {
        header_up X-MITMProxy-Host        {host}
        header_up X-MITMProxy-Real-IP     {remote_host}
        header_up X-MITMProxy-Real-Proto  {scheme}
        header_up -Via
        header_up -X-Forwarded-For
        header_up -X-Forwarded-Host
        header_up -X-Forwarded-Proto
        header_down -X-Powered-By
        header_down -Via
    }
}

# Apex domain: info page
example.com {
    import acme_dns
    root * /var/www/html/
    rewrite * /info.html
    file_server
}

http://example.com {
    root * /var/www/html/
    rewrite * /info.html
    file_server
}

# Front-end proxy: intercept all traffic, forward to mitmproxy
*.example.com {
    import acme_dns
    import mitm_proxy
}

http://*.example.com {
    import mitm_proxy
}

# Back-end server: internal target for mitmproxy (no SSL needed)
:8000 {
    root * /var/www/html/

    # Block .git access
    @git path_regexp ^/\.git
    respond @git 403

    # CORS preflight
    @preflight method OPTIONS
    handle @preflight {
        header Access-Control-Allow-Origin  *
        header Access-Control-Allow-Methods "GET, POST, OPTIONS"
        header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Pragma,x-xsrf-token,x-session-id"
        header Access-Control-Max-Age       1728000
        respond "" 204
    }

    # CORS for GET/POST
    @cors method GET POST
    header @cors Access-Control-Allow-Origin   *
    header @cors Access-Control-Allow-Methods  "GET, POST, OPTIONS"
    header @cors Access-Control-Allow-Headers  "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Pragma,x-xsrf-token,x-session-id"
    header @cors Access-Control-Expose-Headers "Content-Length,Content-Range"

    # Rewrite non-existing paths to /index.php
    @notFound not file {path} {path}/
    rewrite @notFound /index.php

    # Pass .php files to PHP-FPM
    @php path *.php
    reverse_proxy @php php:9000 {
        transport fastcgi {
            split .php
        }
    }

    # Serve static files (html, css, js, images, etc.)
    file_server

    # 403/405 → index.php
    handle_errors 403 405 {
        rewrite * /index.php
        php_fastcgi php:9000
    }
}
