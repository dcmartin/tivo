#!/bin/csh
set API = "container"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set TTL = `echo "60 * 60 * 24" | bc`
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
endif
if ($?TIVO == 0) set TIVO = 20

set XML = "$TMP/tivo-$API.$TIVO.$DATE.xml"
if (! -e "$XML") then
    rm -f "$TMP"/tivo-"$API"."$TIVO".*.xml
    curl -s -k --anyauth -u tivo:$MAK "https://$LAN.$TIVO/TiVoConnect?Command=QueryContainer" | sed 's@TiVoContainer xmlns="http://www.tivo.com/developer/calypso-protocol-1.6/"@TiVoContainer@' >! "$XML"
endif
# HTTP header
echo "Content-type: text/xml"
set AGE = `echo "$SECONDS - $DATE" | bc`
echo "Age: $AGE"
echo "Cache-Control: max-age=$TTL"
echo -n "Last-Modified: "
date -r "$DATE"
echo ""
/usr/local/bin/xml fo "$XML"
