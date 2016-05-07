#!/bin/csh
set API = "details"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set TTL = 900
set MAK = `cat ~$USER/.tivodecode_mak`
set TMP = "/Volumes/RAID10/TIVO"
if (! -e "$TMP") set TMP = "/tmp"
# get time
set SECONDS = `date "+%s"`
set DATE = `echo $SECONDS \/ $TTL \* $TTL | bc`

if ($?QUERY_STRING) then
    set TIVO = `echo $QUERY_STRING | sed "s/.*port=\(..\).*/\1/"`
    if ($TIVO > 24) set TIVO = 24
    if ($TIVO < 20) set TIVO = 20
    set ID = `echo $QUERY_STRING | sed "s/.*id=\(.*\)/\1/"`
    if ($#ID == 0) unset ID
endif

set NOTFOUND = "<h2>Resource Not Found</h2>"

if ($?TIVO && $?ID) then
    # set output
    set XML = "$TMP/tivo-$API.$TIVO.$ID.$DATE.xml"
    if (! -e "$XML") then
        rm -f "$TMP/tivo-$API.$TIVO.$ID".*.xml
	curl -o "$XML.$$" -k --anyauth -u tivo:$MAK "https://$LAN.$TIVO"":443/TiVoVideoDetails?id=$ID" 
	if (-e "$XML.$$") then
	   # check to see if failure
	   look "$NOTFOUND" "$XML.$$"
	   if ($status != 0) then
	       cat "$XML.$$" | sed "s/'//g" | sed "s/,//g" >! "$XML"
	   endif
	   rm -f "$XML.$$"
	endif
    endif
endif
if (-e "$XML") then
    echo "Content-type: text/xml"
    set AGE = `echo "$SECONDS - $DATE" | bc`
    echo "Age: $AGE"
    echo "Cache-Control: max-age=$TTL"
    echo -n "Last-modified: "
    date -r "$DATE"
    echo ""
    /usr/local/bin/xml fo "$XML"
else
    echo "Status: 404 Not Found"
    echo "Content-type: text/html"
    echo ""
    echo "<html><body><h2>Not Found: TiVo ($TIVO) Id ($ID)</body></html>"
endif
