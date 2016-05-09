#!/bin/csh
set API = "csv"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set TTL = 900
set MAK = `cat ~$USER/.tivodecode_mak`
set TMP = "/Volumes/RAID10/TIVO"
if (! -e "$TMP") set TMP = "/tmp"
# get time
set SECONDS = `date "+%s"`
set DATE = `echo $SECONDS \/ $TTL \* $TTL | bc`

# parse QUERY_STRING
if ($?QUERY_STRING) then
    set TIVO = `echo $QUERY_STRING | sed "s/.*port=\(..\).*/\1/"`
    if ($TIVO > 24) set TIVO = 24
    if ($TIVO < 20) set TIVO = 20
endif
if ($?TIVO == 0) set TIVO = 20

set MIXPANELJS = "http://$WWW/CGI/script/mixpanel.js"

# set output
set OUT = "$TMP/tivo-$API.$TIVO.$DATE.csv"
if (! -e "$OUT") then
    # remove old OUT
    rm -f "$TMP/tivo-$API.$TIVO".*.csv
    touch "$OUT"
    # temporary XML for containers
    set XML = "$TMP/tivo-$API.$$.xml"
    # get XML for all TiVos
    curl -s -o "$XML" "http://$WWW/CGI/tivo-nowplaying.cgi?port=$TIVO"
    set XMLSIZ = `wc -c "$XML" | awk '{ print $1 }'`
    if (-e "$XML" && $XMLSIZ > 0) then
	# XPATH
	set ITEM = "TiVoContainer/Item"
	set LINKS = ( "$ITEM/Links/Content/Url" "ITEM/Links/TiVoVideoDetails/Url" )
	set XSL = "$TMP/tivo-$API.$$.xsl"

	# intiate XSL output file
	echo '<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">' >! "$XSL"
	echo '<xsl:template match="/">' >> "$XSL"
	# echo '<xsl:text disable-output-escaping="yes">\&amp;quot;</xsl:text><xsl:text disable-output-escaping="yes">&amp;#44;</xsl:text>' >> "$XSL"

	# derive all DETAILS
	set DETAILS = ( `/usr/local/bin/xml el -u "$XML" | egrep "$ITEM/Details/" | sed "s@.*/\([^/]*\)@\1@"` )
	foreach i ( $DETAILS )
	    # output header element
	    echo -n "$i", >> "$XSL"
	end
	# add headers for Content & VideoDetails URLs
	echo -n Stream,VideoDetails >> "$XSL"
	# initiate for-select over Item Details
	echo '<xsl:for-each select="/TiVoContainer/Item">' >> "$XSL"
	# set sort options
	echo '<xsl:sort select="Details/Title"/>' >> "$XSL"
	echo '<xsl:sort select="Details/CaptureDate"/>' >> "$XSL"
	echo '<xsl:sort select="Details/EpisodeTitle"/>' >> "$XSL"
	# iterate over all details
	foreach i ( $DETAILS )
	    echo -n \""<xsl:value-of select="\""Details/$i"\""/>"\", >> "$XSL"
	end
	# add Content and TiVoVideoDetails links
	echo -n '"<xsl:value-of select="Links/Content/Url"/>",' >> "$XSL"
	echo -n '"<xsl:value-of select="Links/TiVoVideoDetails/Url"/>"' >> "$XSL"
	# end XSL file
	echo '</xsl:for-each></xsl:template></xsl:stylesheet>' >> "$XSL"
	# process XML via XSL into HTML
	/usr/local/bin/xml tr "$XSL" "$XML" >! "$OUT"
	# remove XSL & XML
	# rm -f "$XSL" "$XML"
    endif
endif
set OUTSIZE = `wc -c $OUT | awk '{ print $1 }'`
if (-e "$OUT" && $OUTSIZE > 0) then
    # HTTP header
    echo "Content-Type: text/csv"
    set AGE = `echo "$SECONDS - $DATE" | bc`
    echo "Age: $AGE"
    echo "Cache-Control: max-age=$TTL"
    echo -n "Last-Modified: "
    date -r "$DATE" '+%a, %d %b %Y %H:%M:%S %Z'
    echo ""
    tail +3 "$OUT"
else if (-e "$OUT") then
    rm "$OUT"
else
    echo "Status: 202 Accepted"
    echo ""
endif
