//
// Do any local configuration here
//

// Consider adding the 1918 zones here, if they are not used in your
// organization
//include "/etc/bind/zones.rfc1918";

key "acme-key" {
    algorithm hmac-sha256;
    secret "TSIG_SECRET_PLACEHOLDER";
};

zone "example.com" {
    type master;
    file "/var/cache/bind/zonefile.db";
    notify no;
    allow-update { key "acme-key"; };
};