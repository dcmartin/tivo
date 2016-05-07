#!/bin/csh
set API = "allnowplaying"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set TTL = 10
set MAK = `cat ~$USER/.tivodecode_mak`
set TMP = "/Volumes/RAID10/TIVO"
if (! -e "$TMP") set TMP = "/tmp"
# get time
set SECONDS = `date "+%s"`
set DATE = `echo $SECONDS \/ $TTL \* $TTL | bc`

set TIVOPORTS = ( 20 21 22 23 24 )

# check output
set OUT = "$TMP/tivo-$API.$DATE.xml"

# check for cache
if (! -e "$OUT") then
    # remove all old output
    rm -f "$TMP"/tivo-"$API".*.xml; touch "$OUT"
    # XML header
    set XMLHEADER = '<?xml version="1.0" encoding="utf-8"?>'
    # Initiate output
    echo "$XMLHEADER<TiVoContainerList><Details><TotalItems>$#TIVOPORTS</TotalItems></Details>" >! "$OUT".$$

    # Loop over all TiVos by port #
    foreach TIVO ( $TIVOPORTS )
	set XML = "$TMP/tivo-$API.$TIVO.$DATE.$$.xml"
	# get NowPlaying
	curl -s "http://$WWW/CGI/tivo-nowplaying.cgi?port=$TIVO" -o "$XML"
	set XMLVAL = `( /usr/local/bin/xml val -q "$XML"; echo $status )`
	if ($XMLVAL == 0) then
	    tail +2 "$XML" >> "$OUT".$$
	else
	    # partial results
	    set TTL = 0
	endif
	rm -f "$XML"
    end
    echo "</TiVoContainerList>" >> "$OUT".$$
    mv -f "$OUT".$$ "$OUT"
endif

if (-e "$OUT") then
    set XMLVAL = `( /usr/local/bin/xml val -q "$OUT"; echo $status )`
    if ($XMLVAL == 0) then
	echo "Content-Type: text/xml"
	set AGE = `echo "$SECONDS - $DATE" | bc`
	echo "Age: $AGE"
	echo "Cache-Control: max-age=$TTL"
	echo -n "Last-Modified: "
	date -r "$DATE"
	echo ""
	# dump output
	/usr/local/bin/xml fo "$OUT"
	exit
    endif
else
    echo "Status: 202 Accepted"
    echo ""
endif
