#!/bin/csh
set API = "nowplaying"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set TTL = 900
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

set XML = "$TMP/tivo-$API.$TIVO.$DATE.xml"
if (-e "$XML") then
    set XMLVAL = `( /usr/local/bin/xml val -q "$XML"; echo $status )`	
    if ($XMLVAL != 0) then
	echo "$API -- Invalid XML -- removing $XML" >>! $TMP/LOG
        rm -f "$XML"
    endif
endif
if (! -e "$XML") then
    echo "$API -- Initiating new nowplaying $TIVO" >>! $TMP/LOG
    ./bin/nowplaying.bash
endif

set XML = ( `ls -1t "$TMP/tivo-$API.$TIVO".*.xml` )

if ($#XML == 0) then
    echo "Status: 202 Accepted"
    echo ""
else if ($#XML > 0) then
    if (-e "$XML[1]") then
	echo "Content-Type: text/xml"
	set AGE = `echo "$SECONDS - $DATE" | bc`
	echo "Age: $AGE"
	echo "Cache-Control: max-age=$TTL"
	echo -n "Last-Modified: "
	date -r "$DATE" '+%a, %d %b %Y %H:%M:%S %Z'
	echo ""
	echo "$API -- Using $XML[1]" >>! $TMP/LOG
	cat "$XML[1]"
	if ($#XML > 1) rm -f $XML[2-]
    else
	echo "$API -- In progress: $XML[1]" >>! $TMP/LOG
	echo "Status: Accepted"
	echo ""
    endif
endif
