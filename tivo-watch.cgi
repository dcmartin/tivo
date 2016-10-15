#!/bin/csh
set API = "watch"
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
    set MPG = "$TMP/MPG/tivo-stream.$TIVO.$ID.$DATE.mpg"
endif

# check if done and good
if ($?MPG && -e "$MPG") then
    # output
    echo "Content-Type: video/mpeg"
    echo "Content-Location: http://www.dcmartin.com/TIVO/$MPG:t"
    set AGE = `echo "$SECONDS - $DATE" | bc`
    echo "Age: $AGE"
    echo "Cache-Control: max-age=$TTL"
    echo -n "Last-Modified: "
    date -r "$DATE" '+%a, %d %b %Y %H:%M:%S %Z'
    echo -n "Content-Disposition: Attachment; filename="
    echo "$MPG:t"
    echo -n "Content-Length: "
    wc -c "$MPG" | awk '{ print $1 }'
    echo ""
    dd if="$MPG" bs=1k
else
    set TMPMPG = ( `echo "$TMP/MPG/tivo-stream.$TIVO.$ID".*.mpg.*` )
    # output
    echo "Status: 206 Partial Content"
    echo "Content-Type: video/mpeg"
    echo "Content-Location: http://www.dcmartin.com/TIVO/$MPG:t"
    echo "Age: 0"
    echo "Cache-Control: max-age=0"
    echo -n "Last-Modified: "
    date -r "$SECONDS" '+%a, %d %b %Y %H:%M:%S %Z'
    echo -n "Content-Disposition: Attachment; filename="
    echo "$MPG:t"
    echo ""
    tail -c +0 -f "$TMPMPG"
endif
