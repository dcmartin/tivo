#!/bin/csh
set API = "name"
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
endif
if ($?TIVO == 0) set TIVO = 20

set N = TIVO$TIVO
set XML = "$TMP/tivo-name.$TIVO.xml"
curl -s -o "$XML" "http://www.dcmartin.com/CGI/tivo-container.cgi?port=$TIVO"
set XMLSIZ = `wc "$XML" | awk '{ print $1 }'`
if (-e "$XML" && $XMLSIZ > 0) then
    set P = "/TiVoContainer/Details/TotalItems"
    set TI = ( `/usr/local/bin/xml sel -t -v $P "$XML"` )
    if ($TI > 0) then
	set P = "/TiVoContainer/Item/Details/UniqueId"
	set TN = ( `/usr/local/bin/xml sel -t -v $P "$XML" | sed 's/,/\&#44;/g' | sed 's/"/\&quot;/g' | sed 's/ //g' | sed 's/^\(.*\)\n/"\1"/'` )
	if ($#TN == $TI) set N = $TN[$TI]
    endif
endif
echo "Content-type: text/text"
echo ""
echo "$N"
