<?php

// hostname gets passed from mitmproxy in X-MITMProxy-Host
$hostname = $_SERVER['HTTP_X_MITMPROXY_HOST'];

$blacklist = file("/data/blacklist.txt");

# exit if the hostname is blacklisted
foreach($blacklist as $b) {
    if(-1 < strpos($hostname, trim($b))) { die("blacklisted"); }
}

# not requesting the configured hostname
if( -1 >= strpos($hostname, $_ENV['DOMAIN'])) {
    http_response_code(503);
    die();
}

echo "The page " . htmlentities($_SERVER['REQUEST_URI']) . " was requested but not found. ";
echo "Add the file under /www to serve your own custom content.";

?>