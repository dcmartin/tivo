#!/bin/csh
echo "Content-type: text/xml"
echo ""
if ($?QUERY_STRING) then
    set TIVO = `echo $QUERY_STRING | sed "s/.*port=\(..\).*/\1/"`
else
    set TIVO = 20
endif
if ($TIVO > 23) then
    set TIVO = 20
endif
if ($TIVO < 20) then
    set TIVO = 20
endif
set DATE=`date "+%H%M"`
set OUTPUT = "/tmp/tivo.$TIVO.$DATE"
if (! -e "$OUTPUT") then
    rm /tmp/tivo.$TIVO.*
    curl -o "$OUTPUT.$$" -k --anyauth -u tivo:$MAKID "https://192.168.1.$TIVO/TiVoConnect?Command=QueryContainer&Container=%2FNowPlaying&Recurse=Yes" 
    if (-e "$OUTPUT.$$") then
        cat "$OUTPUT.$$" | sed "s/http:\/\/192.168.1.\([0-9]*\):80\/download\/\([^?]*\)?/http:\/\/www.dcmartin.com\/CGI\/TiVoVideoDownload.cgi?port=\1\&amp;show=\2\&amp;/g" | sed "s/https:\/\/192.168.1.\([0-9]*\):443\/TiVoVideoDetails?id=\([0-9]*\)/http:\/\/www.dcmartin.com\/CGI\/TiVoVideoDetails.cgi?port=\1\&amp;id=\2/g" >! "$OUTPUT"
        rm "$OUTPUT.$$"
        cat "$OUTPUT"
    endif
else
    cat "$OUTPUT"
endif
echo ""
