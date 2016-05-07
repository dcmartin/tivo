#!/bin/csh
set API = "expirationTime"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set TTL = 1800
set MAK = `cat ~$USER/.tivodecode_mak`
set TMP = "/Volumes/RAID10/TIVO"
if (! -e "$TMP") set TMP = "/tmp"
# get time
set SECONDS = `date "+%s"`
set DATE = `echo $SECONDS \/ $TTL \* $TTL | bc`

# parse QUERY_STRING
if ($?QUERY_STRING) then
    set TIVO = `echo $QUERY_STRING | sed "s/.*port=\(..\).*/\1/"`
    if ($TIVO > 24) set TIVO = 24
    if ($TIVO < 20) set TIVO = 20
    set ID = `echo $QUERY_STRING | sed "s/.*id=\(.*\).*/\1/"`
endif
if ($?TIVO == 0) set TIVO = 20
if ($?ID == 0) set ID = 0

set XML = "$TMP/tivo-$API.$TIVO.$ID.$DATE.xml"
if (! -e "$XML") then
    curl -s -o "$XML" "http://www.dcmartin.com/CGI/tivo-details.cgi?port=$TIVO&id=$ID"
endif
if (-e "$XML") then
    set XMLSIZ = `wc "$XML" | awk '{ print $1 }'`
else
    set XMLSIZ = 0
endif

set N = ""
if (-e "$XML" && $XMLSIZ > 0) then
    set P = "TvBusMarshalledStruct:TvBusEnvelope/expirationTime"
    set TI = ( `/usr/local/bin/xml sel -t -v $P "$XML"` )
    if ($#TI > 0) then
	set tz = `date "+%z"`
	set hr = `echo $tz / 100 | bc`
	set N = `date -j -v "$hr"H -f "%Y-%m-%dT%H:%M:%SZ" "$TI"`
    endif
endif
echo "Content-type: text/text"
echo ""
echo "$N"
