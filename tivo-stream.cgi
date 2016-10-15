#!/bin/csh
set API = "stream"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set MAK = `cat ~$USER/.tivodecode_mak`
# 90 days 
set TTL = `echo "60 * 60 * 24 * 90" | bc`
set TMP = "/Volumes/NITRO/TIVO"
if (! -e "$TMP") set TMP = "/tmp"
# get time
set SECONDS = `date "+%s"`
set DATE = `echo $SECONDS \/ $TTL \* $TTL | bc`

if ($?QUERY_STRING != 0) then
    set TIVO = `echo $QUERY_STRING | sed "s/.*port=\(..\).*/\1/"`
    if ($TIVO < 20 || $TIVO > 24) unset TIVO
    set ID = `echo $QUERY_STRING | sed "s/.*id=\([0-9]*\).*/\1/"`
endif

if ($?TIVO && $?ID) then
    set MPG = "$TMP/MPG/tivo-$API.$TIVO.$ID.$DATE.mpg"
endif

set NOTFOUND = "<h2>Resource Not Found</h2>"
set FORBIDDEN = "<h2>Access Forbidden</h2>"
set SERVERBUSY = "<h2>Server Busy</h2>"

if ($?MPG == 0) then
    set ERROR = "<h2>INVALID TIVO ($TIVO) AND ID ($ID)</h2>"
    goto done
endif

set copyProtected = `curl -s "http://$WWW/CGI/tivo-copyProtected.cgi?$QUERY_STRING"`
if ($copyProtected == "true") then
    set ERROR = "COPY PROTECTED"
    goto done
endif

# Check if this TiVo is currently busy on any ID or DATE
set INPROGRESS = ( `echo "$TMP/MPG/tivo-$API.$TIVO".*.mpg.*` )
 
if (! -e "$MPG" && $#INPROGRESS == 0) then
    set isEpisode = `curl -s "http://$WWW/CGI/tivo-isEpisode.cgi?$QUERY_STRING"`
    set seriesTitle = `curl -s "http://$WWW/CGI/tivo-seriesTitle.cgi?$QUERY_STRING"`
    set originalAirDate = `curl -s "http://$WWW/CGI/tivo-originalAirDate.cgi?$QUERY_STRING"`

    set EPISODE = "$originalAirDate"
    if ($isEpisode == "true") then
	set episodeNumber = `curl -s "http://$WWW/CGI/tivo-episodeNumber.cgi?$QUERY_STRING"`

	set n = "$episodeNumber"
	if ($n > 0) then
	    set s = `echo "$n / 100" | bc`
	    set e = `echo "$n - ( ( $n / 100) * 100 )" | bc`
	    set EPISODE = `echo $s $e | awk '{ printf "S%02dE%02d", $1, $2 }'`
	else
	endif
	# save output to Plex
	mkdir -p "$TMP/PLEX/$seriesTitle"
	ln -s "$TMP/PLEX/$seriesTitle/$seriesTitle $EPISODE.mpg" "$MPG"
    endif
    # remove old MPGs
    rm -f "$TMP/MPG/tivo-$API.$TIVO.$ID".*.mpg.*

    # set download URL
    set SHOW = `echo "$seriesTitle" | sed "s/ /%20/g" | sed "s/'/%27/g" | sed 's/,/%2c/g' | sed 's/:/%3a/g'`
    set URL = "http://$LAN.$TIVO/download/$SHOW.TiVo?Container=%2FNowPlaying&id=$ID" 
    # get download in separate thread
    ./bin/getshow.bash -m "$MAK" -u "$URL" -o "$TMP/PLEX/$seriesTitle/$seriesTitle $EPISODE.mpg" -x "$MPG.$$"
    # wait 
    sleep 3
endif

# check for in-progress download from this TIVO, ID and DATE 
set TMPMPG = ( `echo "$TMP/MPG/tivo-$API.$TIVO.$ID.$DATE.mpg".*` )

if ($?MPG) then
    # test size
    set MPGSIZ = `ls -l "$MPG" | awk '{ print $5 }'`
    if ($MPGSIZ == 0) then
        set ERROR = "<h2>Zero Size $MPG</h2>"
	rm -f "$MPG"
	goto done
    endif
    # check to see if failure
    look "$NOTFOUND" "$MPG"
    if ($status == 0) then
	set ERROR = ( `cat $MPG` ) 
	rm -f "$MPG"
	goto done
    else
	look "$FORBIDDEN" "$MPG"
	if ($status == 0) then
	    set ERROR = ( `cat $MPG` )
	    rm -f "$MPG"
	    goto done
	else 
	    look "$SERVERBUSY" "$MPG"
	    if ($status == 0) then
		set ERROR = ( `cat $MPG` )
		rm -f "$MPG"
		goto done
	    endif
	endif
    endif
endif

# check if done and good
if (-e "$MPG" || -e "$TMPMPG") then
    echo "Status: 302 Found"
    echo "Location: http://$WWW/CGI/tivo-video.cgi?port=$TIVO&id=$ID"
    echo ""
else
    set ERROR = "<h2>TiVo ($TIVO) Currently In-Progress: $INPROGRESS</h2>"
endif

done:

if ($?ERROR) then
    echo "Content-Type: text/html"
    echo ""
    echo "<html><body>$ERROR</body></html>"
endif
