#!/bin/csh
set API = "show"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set TTL = 2
set MAK = `cat ~$USER/.tivodecode_mak`
set TMP = "/Volumes/RAID10/TIVO"
if (! -e "$TMP") set TMP = "/tmp"
# get time
set SECONDS = `date "+%s"`
set DATE = `echo $SECONDS \/ $TTL \* $TTL | bc`

set SHOW = ""
set ID = ""

# parse QUERY_STRING
if ($?QUERY_STRING) then
    set SHOW = `echo "$QUERY_STRING" | sed "s/.*show=\(.*\)/\1/"`
endif

set MIXPANELJS = "http://$WWW/CGI/script/mixpanel.js"

echo "Content-type: text/html"
echo ""
echo "<html>"
echo '<script type="text/javascript" src="'$MIXPANELJS'"></script><script>mixpanel.track("tivo-'$API'", { "SHOW": "'$SHOW'", "ID": "'$ID'" } );'
echo "</script>"
echo "<body>"

if ($?SHOW) then
    set CSV = "$TMP/tivo-$API.$$.csv"
    curl -s -o "$CSV" "http://$WWW/CGI/tivo-allcsv.cgi"
    egrep "$SHOW" "$CSV"
    rm "$CSV"
endif
echo "</body></html>"
