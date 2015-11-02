#!/bin/csh
echo "Content-type: text/xml"
echo ""
if ($?QUERY_STRING) then
    set TIVO = `echo $QUERY_STRING | sed "s/.*port=\(..\).*/\1/"`
    set ID = `echo $QUERY_STRING | sed "s/.*id=\([0-9]*\).*/\1/"`
    set SHOW = `echo $QUERY_STRING | sed "s/.*show=\(.*\).TiVo.*/\1.TiVo/"`
else
    set TIVO = 20
    set ID = 3043561
    set SHOW = The%20Graham%20Norton%20Show.TiVo
endif
curl --cookie "sid=abc" -k --anyauth -u tivo:$MAKID "http://192.168.1.$TIVO/download/$SHOW?Container=%2FNowPlaying\&id=$ID"
echo ""
