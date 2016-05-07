#!/bin/csh
set API = "download"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set MAK = `cat ~$USER/.tivodecode_mak`
# seven days 
set TTL = `echo "60 * 60 * 24 * 7" | bc`
set TMP = "/Volumes/RAID10/TIVO"
if (! -e "$TMP") set TMP = "/tmp"
# get time
set SECONDS = `date "+%s"`
set DATE = `echo $SECONDS \/ $TTL \* $TTL | bc`

if ($?QUERY_STRING != 0) then
    set TIVO = `echo $QUERY_STRING | sed "s/.*port=\(..\).*/\1/"`
    set ID = `echo $QUERY_STRING | sed "s/.*id=\([0-9]*\).*/\1/"`
    set SHOW = `echo $QUERY_STRING | sed "s/.*show=\([\&]*\).*/\1/"`
    if ($status) unset ID
endif
if ($?TIVO == 0) set TIVO = 20

# set LAST
set LAST = `date`
set NOTFOUND = "<h2>Resource Not Found</h2>"
set FORBIDDEN = "<h2>Access Forbidden</h2>"
set SERVERBUSY = "<h2>Server Busy</h2>"

# set temporary directory
if ($?TIVO && $?ID) then
    set MPG = "$TMP/tivo-$API.$TIVO.$ID.mpg"
endif
if ($?MPG) then
    if (! -e "$MPG") then
	# check to see if MPG is in process
	set RAW = "$TMP/tivo-$API.$TIVO.$ID.raw"
	if (! -e "$RAW") then
	    # test if in progress
	    set INPROGRESS = `echo "$RAW".*`
	    if ($#INPROGRESS == 0) then
		# get metadata
		set CSV = "$TMP/tivo-$API.$TIVO.csv"
		curl -s "http://$WWW/CGI/tivo-csv.cgi?port=$TIVO" >! "$CSV".$$
		set COLS = ( `head -1 "$CSV".$$ | sed "s/,/ /g"` )
		cat "$CSV".$$ | egrep "$ID" >! "$CSV"
		set j = 1
		foreach i ( $COLS )
		    if ( $i == "SourceSize" ) then
		    	set source = $j
		    else if ( $i == "CaptureDate" ) then
		        set capture = $j
		    else if ( $i == "Content" ) then
		    	set content = $j
		    endif
		    set j = `echo "$j + 1" | bc`
		end
		# Content,CaptureDate,SourceSize,Title == 1,4,21,28
		set SHOW = `cut -f $content -d , "$CSV" | sed "s/.*show=\([^\&]*\).*/\1/"`
		set LAST = `cut -f $capture -d , "$CSV" | xargs -n 1 date -r`
		set SSIZ = `cut -f $source -d , "$CSV"`
		rm -f "$CSV" "$CSV".$$
		echo "Running download" $RAW $SSIZ $SHOW >>! $TMP/LOG
		date >>! $TMP/LOG
		# ./doit -r "$RAW.$$" -u "http://$LAN.$TIVO/download/$SHOW.TiVo?Container=%2FNowPlaying\&id=$ID" < /dev/null >&! /dev/null &
		(  curl -o "$RAW.$$" -s --cookie "sid=abc" -k --anyauth -u tivo:$MAK "http://$LAN.$TIVO/download/$SHOW.TiVo?Container=%2FNowPlaying\&id=$ID"; mv "$RAW.$$" "$RAW" ) < /dev/null >&! /dev/null &
		echo "Status: " $status >>! $TMP/LOG
		# calculate size in bytes
		echo "Size: " `wc -c "$RAW" | awk '{ print $1 }'` >>! $TMP/LOG
		date >>! $TMP/LOG
		goto done
	    endif
	else if (! -e "$MPG") then
	    # check to see if failure
	    look "$NOTFOUND" "$RAW"
	    if ($status != 0) then
		look "$FORBIDDEN" "$RAW"
		if ($status == 0) then
		    set ERROR = "$FORBIDDEN"
		    rm -f "$RAW"
		else 
		    look "$SERVERBUSY" "$RAW"
		    if ($status == 0) then
		        set ERROR = "$SERVERBUSY"
			rm -f "$RAW"
		    endif
		endif
	    else	
		set ERROR = "$NOTFOUND"
		rm "$RAW"
	    endif
	    set TTS = "$TMP/tivo-$API.$TIVO.$ID.tts"
	    if (-e "$RAW" && ! -e "$TTS") then
		# test if in progress
		set INPROGRESS = `echo $TTS.*`
		if ($#INPROGRESS == 0) then
		    # convert to MPEG
		    echo "Running decode" $TTS.$$ >>! $TMP/LOG
		    ( /usr/local/bin/tivodecode -m $MAK -o "$TTS.$$" "$RAW"; mv "$TTS.$$" "$TTS" ) < /dev/null >&! /dev/null &
		    echo "Status: " $status >>! $TMP/LOG
		    goto done
		endif
	    else if (-e "$TTS") then
		mv -f "$TTS" "$MPG"
		# remove RAW
		rm -f "$RAW"
	    endif
	endif
    endif
done:
    if (-e "$MPG") then
	# calculate size in bytes
	set MPGSIZ = `wc -c "$MPG" | awk '{ print $1 }'`
	echo "Content-Type: video/mpeg"
	set AGE = `echo "$SECONDS - $DATE" | bc`
	echo "Age: $AGE"
	echo "Cache-Control: max-age=$TTL"
	echo -n "Last-Modified: "
	echo "$LAST"
	echo -n "Content-Length: "
	echo "$MPGSIZ"
	echo ""
	dd if="$MPG"
    else if ($?ERROR) then
	echo "Content-Type: text/html"
	echo ""
	echo "<html><body>$ERROR</body></html>"
    else
	echo "Content-type: text/html"
	echo ""
	echo "<html><body><h2>IN PROCESS</h2></body></html>"
    endif
endif
