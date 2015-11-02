#!/bin/csh
echo "Content-type: text/xml"
echo ""
if ($?QUERY_STRING) then
    set TIVO = `echo $QUERY_STRING | sed "s/.*port=\(..\).*/\1/"`
    set ID = `echo $QUERY_STRING | sed "s/.*id=\(.*\)/\1/"`
else
    set TIVO = 20
    set ID = 3043561
endif
set DATE = `date "+%H:%M"`
set OUTPUT = "/tmp/TiVoVideoDetails.$TIVO.$ID.$DATE"
if (! -e "$OUTPUT") then
    rm -f $OUTPUT:r.*
    curl -o "$OUTPUT" -k --anyauth -u tivo:$MAKID "https://192.168.1.$TIVO"":443/TiVoVideoDetails?id=$ID" 
endif
if (-e "$OUTPUT") then
    cat "$OUTPUT"
    echo ""
endif
