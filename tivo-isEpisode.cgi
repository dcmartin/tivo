#!/bin/csh
set API = "isEpisode"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set TTL = 1800
set MAK = `cat ~$USER/.tivodecode_mak`
set TMP = "/Volumes/NITRO/TIVO"
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

set N = ""
set XML = "$TMP/tivo-$API.$TIVO.$ID.xml"
curl -s -o "$XML" "http://www.dcmartin.com/CGI/tivo-details.cgi?port=$TIVO&id=$ID"
set XMLSIZ = `wc "$XML" | awk '{ print $1 }'`
if (-e "$XML" && $XMLSIZ > 0) then
    set P = "TvBusMarshalledStruct:TvBusEnvelope/showing/program/isEpisode" 
    set TI = ( `/usr/local/bin/xml sel -t -v $P "$XML"` )
    if ($#TI > 0) then
	set N = $TI 
    endif
endif
rm -f "$XML"
echo "Content-type: text/text"
echo ""
echo "$N"
