#!/bin/csh
set APP = "tivo"
set API = "video"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set TTL = 2
set MAK = `cat ~$USER/.tivodecode_mak`
set TMP = "/Volumes/NITRO/TIVO"
if (! -e "$TMP") set TMP = "/tmp"
# get time
set SECONDS = `date "+%s"`
set DATE = `echo $SECONDS \/ $TTL \* $TTL | bc`

set TIVO = ""
set ID = ""

# parse QUERY_STRING
if ($?QUERY_STRING) then
    set TIVO = `echo "$QUERY_STRING" | sed "s/.*port=\(2[0-4]\).*/\1/"`
    set ID = `echo "$QUERY_STRING" | sed "s/.*id=\([0-9]*\).*/\1/"`
endif

echo "BEGIN: $APP-$API -- $$" >>! $TMP/LOG

set MIXPANELJS = "http://$WWW/CGI/script/mixpanel.js"

echo "Content-type: text/html"
echo ""
echo "<html>"
echo '<script type="text/javascript" src="'$MIXPANELJS'"></script><script>mixpanel.track("tivo-'$API'", { "TIVO": "'$TIVO'", "ID": "'$ID'" } );'
echo "</script>"
echo "<body>"

if ($?TIVO && $?ID) then
    set MPG = ( `echo "$TMP/MPG/tivo-stream.$TIVO.$ID".*.mpg` )
    if (! -e "$MPG") set MPG = ( `echo "$TMP/MPG/tivo-stream.$TIVO.$ID".*.mpg.*` )
    if ($#MPG == 1 && -e "$MPG") then
	# set URL = "http://$WWW/CGI/tivo-watch.cgi?port=$TIVO\&id=$ID"
	set URL = "http://$WWW/TIVO/$MPG:t"
	echo "$URL" | awk '{ printf "<video width=\"100%%\" controls autoplay src=\"%s\" type=\"video/mpeg\"/>\n</video>\n<p><strong>Download</strong>: <a href=\"%s\">MPEG</a></p>\n", $1, $1, $1 }'
    else
	echo "<h2>Not found: $TIVO $ID $DATE</h2>"
    endif
else
    echo "<h2>Not specified: $TIVO $ID</h2>"
endif
echo "</body></html>"

echo "FINISH: $APP-$API -- $$" >>! $TMP/LOG
