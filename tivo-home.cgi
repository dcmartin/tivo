#!/bin/csh
set API = "home"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set TTL = 60
set MAK = `cat ~$USER/.tivodecode_mak`
set TMP = "/Volumes/RAID10/TIVO"
if (! -e "$TMP") set TMP = "/tmp"
# get time
set SECONDS = `date "+%s"`
set DATE = `echo $SECONDS \/ $TTL \* $TTL | bc`

# parse query string
if ($?QUERY_STRING) then
    set TIVO = `echo $QUERY_STRING | sed "s/.*port=\(..\).*/\1/"`
    if ($TIVO > 24) set TIVO = 24
    if ($TIVO < 20) set TIVO = 20
endif
if ($?TIVO == 0) set TIVO = 20

if (! -e "$TMP/tivo-$API.$DATE.html") then
    echo "$API -- Initiating bin/$API" >>! $TMP/LOG
    ./bin/home.bash
endif

set HTML = ( `ls -1t "$TMP/tivo-$API".*.html` )

if ($#HTML == 0) then
    echo "$API -- Returning Accepted: $HTML" >>! $TMP/LOG
    echo "Status: 202 Accepted"
    echo "Content-Type: text/html"
    echo ""
    echo "<html><body><h2>ACCEPTED</h2></body></html>"
else if ($#HTML > 0) then
    if (-e "$HTML[1]") then
	echo "Content-Type: text/html"
	echo "Refresh: $TTL"
	set AGE = `echo "$SECONDS - $DATE" | bc`
	echo "Age: $AGE"
	echo "Cache-Control: max-age=$TTL"
	echo -n "Last-Modified: "
	date -r "$DATE"
	echo ""
	echo "$API -- Using $HTML[1]" >>! $TMP/LOG
	cat "$HTML[1]"
	if ($#HTML > 1) rm -f $HTML[2-]
    else
	echo "$API -- Processing $HTML" >>! $TMP/LOG
	echo "Content-Type: text/html"
	echo ""
	echo "<html><body><h2>IN PROGRESS</h2></body></html>"
    endif
endif
