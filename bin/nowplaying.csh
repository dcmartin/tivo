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
set XMLTMP = ( `echo "$XML".*` )

if (! -e "$XML" && $#XMLTMP == 0) then
    echo "bin/$API -- Making $XML" >>! $TMP/LOG
    touch "$XML.$$"
    # get TiVo name
    set TIVONAME = `curl -s "http://www.dcmartin.com/CGI/tivo-name.cgi?port=$TIVO"`
    # get NowPlaying container
    curl -o "$XML.$$.$$" -s -k --anyauth -u "tivo:$MAK" "https://$LAN.$TIVO/TiVoConnect?Command=QueryContainer&Container=%2FNowPlaying&Recurse=Yes"
    set XMLVAL = `( /usr/local/bin/xml val -q "$XML.$$.$$"; echo $status )`
    if ($XMLVAL == 0) then
	cat "$XML.$$.$$" | \
    	    sed 's@TiVoContainer xmlns="http://www.tivo.com/developer/calypso-protocol-1.6/"@TiVoContainer@' | \
	    /usr/local/bin/xml ed -i "/TiVoContainer/Item/Details/ContentType" -t elem -n TiVoName -v "$TIVONAME" | \
	    /usr/local/bin/xml ed -u "/TiVoContainer/Details/UniqueId" -v "$TIVONAME" >! "$XML.$$"
	rm -f "$XML.$$.$$"
	# get total items
	set totalitems = `/usr/local/bin/xml sel -t -v "/TiVoContainer/Details/TotalItems" "$XML.$$"`
	# get & set last change
	set lastchg = `/usr/local/bin/xml sel -t -v "/TiVoContainer/Details/LastChangeDate" "$XML.$$"`
	set LASTCHANGE = `date -r $lastchg`
	# set LASTCHANGE
	cat "$XML.$$" | /usr/local/bin/xml ed -i "/TiVoContainer/Item/Details/ContentType" -t elem -n LastChange -v "$LASTCHANGE" >! "$XML.$$.$$"
	mv -f "$XML.$$.$$" "$XML.$$"
	# start output
	head -14 "$XML.$$" >! "$XML.$$.$$"
	# initialize for iteration
	set item = 0
	# iterate
	while ($item < $totalitems)
	    set itemstart = `/usr/local/bin/xml sel -t -v "/TiVoContainer/ItemStart" "$XML.$$"`
	    set itemcount = `/usr/local/bin/xml sel -t -v "/TiVoContainer/ItemCount" "$XML.$$"`
	    set item = `echo "$itemstart + $itemcount + 1" | bc`
	    set lines = `tail +15 "$XML.$$" | wc | awk '{ print $1 }'`
	    set lines = `echo "$lines - 1" | bc`

	    # sed 's/,/\&#44;/g' | sed 's/"/\&quot;/g' | \
	    tail +15 "$XML.$$" | \
		sed 's/,/ /g' | sed "s/'//g" | sed 's/"//g' | \
		sed "s@http://$LAN.$TIVO\:80/download/\([^?]*\).TiVo?Container=%2FNowPlaying\&amp;id=\([0-9]*\)@http://$WWW/CGI/tivo-stream.cgi?port=$TIVO\&amp;id=\2@g" | \
		sed "s@https://$LAN.$TIVO\:443/TiVoVideoDetails?id=\([0-9]*\)@http://$WWW/CGI/tivo-details.cgi?port=$TIVO\&amp;id=\1@g" | head -$lines >> "$XML".$$.$$

	    curl -o "$XML".$$.$item -s -k --anyauth -u "tivo:$MAK" "https://$LAN.$TIVO/TiVoConnect?Command=QueryContainer&Container=%2FNowPlaying&Recurse=Yes&AnchorOffset=$item" 
	    set XMLVAL = `( /usr/local/bin/xml val -q "$XML.$$.$item"; echo $status )`
	    if ($XMLVAL == 0) then
		cat "$XML.$$.$item" | \
		    sed 's@TiVoContainer xmlns="http://www.tivo.com/developer/calypso-protocol-1.6/"@TiVoContainer@' | \
		    /usr/local/bin/xml ed -i "/TiVoContainer/Item/Details/ContentType" -t elem -n TiVoName -v "$TIVONAME" | \
		    /usr/local/bin/xml ed -u "/TiVoContainer/Details/UniqueId" -v "$TIVONAME" >! "$XML.$$"
		# cleanup this item
		rm -f "$XML.$$.$item"
	    else
		rm -f "$XML.$$.$item"
		set TTL = 1
		break
	    endif
	    echo "bin/$API -- $XML -- WORKING $item of $totalitems" >>! $TMP/LOG
	end
	rm -f "$XML.$$"
	echo "</TiVoContainer>" >> "$XML.$$.$$"
	mv -f "$XML.$$.$$" "$XML"
	echo "bin/$API -- $XML -- SUCCESS" >>! $TMP/LOG
    else
	rm -f "$XML.$$" "$XML.$$.$$"
	echo "bin/$API -- $XML -- FAILURE" >>! $TMP/LOG
    endif
else
    echo "bin/$API -- $XML -- PROCESSING" >>! $TMP/LOG
endif
