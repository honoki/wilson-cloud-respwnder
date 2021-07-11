# mitmproxy config
server {
	listen 80;
	listen [::]:80;
	listen 443 ssl;
	listen [::]:443 ssl;
	
	server_name "*.example.com";
    ssl_certificate         /etc/nginx/keys/fullchain.pem;
    ssl_certificate_key     /etc/nginx/keys/privkey.pem;

	# pass everything on to the mitmproxy container
	location / {
		server_tokens off;
		proxy_set_header X-MITMProxy-Host $host;
		proxy_set_header X-MITMProxy-Real-IP $remote_addr;
		proxy_set_header X-MITMProxy-Real-Proto $scheme;
		proxy_pass http://mitmproxy:30001;
		proxy_hide_header X-Powered-By;
	}

}

# reverse proxy config
server {
	listen *:8000;

	root /var/www/html/;
	index index.php;

	location / {
		
		try_files $uri /catchall;
		if ($request_method = 'OPTIONS') {
			add_header 'Access-Control-Allow-Origin' '*';
			add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
			add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
			add_header 'Access-Control-Max-Age' 1728000;
			add_header 'Content-Type' 'text/plain; charset=utf-8';
			add_header 'Content-Length' 0;
			return 204;
		}
		if ($request_method = 'POST') {
			add_header 'Access-Control-Allow-Origin' '*';
			add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
			add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
			add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range';
		}
		if ($request_method = 'GET') {
			add_header 'Access-Control-Allow-Origin' '*';
			add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
			add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
			add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range';
		}
	}

    error_page  405     =200 $uri;
    error_page  404     =200 /catchall;
    error_page  403     =200 /catchall;

    # if a file is not found, we serve the index.php page by default
	location /catchall {
		alias /var/www/html/index.php;
        fastcgi_pass php:9000;
		fastcgi_index index.php;
		fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
		include fastcgi_params;
	}

    # make sure PHP files are properly executed
	location ~ \.php$ {
		try_files $uri /catchall;
		fastcgi_pass php:9000;
		fastcgi_index index.php;
		fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
		include fastcgi_params;
	}

}