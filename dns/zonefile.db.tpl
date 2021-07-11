;
; Zone file for your domain
;
; The full zone file
;
$TTL 3D
@       IN      SOA     dns example.com. (
                        200608081       ; serial, todays date + todays serial # 
                        8H              ; refresh, seconds
                        2H              ; retry, seconds
                        4W              ; expire, seconds
                        1D )            ; minimum, seconds
;
            NS      ns              ; Inet Address of name server
ns          A       1.1.1.1
*           A       1.1.1.1
*.sub       A       1.1.1.1
*           TXT     "I'm a custom text record"
test.sub    TXT     "ohyeah"
