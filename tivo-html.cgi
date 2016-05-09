#!/bin/csh
set API = "html"
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
set OUT = "$TMP/tivo-$API.$TIVO.$DATE.html"
if (! -e "$OUT") then
    # remove old OUT
    rm -f "$TMP/tivo-$API.$TIVO".*.html
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
	echo '<?xml version="1.0" encoding="UTF-8"?><xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">' >! "$XSL"
	echo '<xsl:template match="/"><html>' >> "$XSL"
	echo '<script type="text/javascript" src="'$MIXPANELJS'"></script><script>mixpanel.track('"'"tivo-$API"');</script>" >> "$XSL"
	echo '<title>Now Playing</title><body><h2>Now Playing</h2><table border="1"><tr bgcolor="#9acd32">' >> "$XSL"

	# derive all DETAILS
	set DETAILS = ( `/usr/local/bin/xml el -u "$XML" | egrep "$ITEM/Details/" | sed "s@.*/\([^/]*\)@\1@"` )
	foreach i ( $DETAILS )
	    # output header element
	    echo "<th>$i</th>" >> "$XSL"
	end
	# add headers for Content & VideoDetails URLs
	echo "<th>Stream</th><th>VideoDetails</th>" >> "$XSL"
	# complete header row; initiate for-select over Item Details
	echo '</tr><xsl:for-each select="/TiVoContainer/Item">' >> "$XSL"
	# set sort options
	echo '<xsl:sort select="Details/Title"/>' >> "$XSL"
	echo '<xsl:sort select="Details/CaptureDate"/>' >> "$XSL"
	echo '<xsl:sort select="Details/EpisodeTitle"/>' >> "$XSL"
	# iterate over all details
	echo '<tr>' >> "$XSL"
	foreach i ( $DETAILS )
	    echo $i | awk '{ OFS=""; printf "<td><xsl:value-of select=\"Details/%s\"/></td>\n", $1 }' >> "$XSL"
	end
	# add Content and TiVoVideoDetails links
	echo '<td><xsl:element name="a"><xsl:attribute name="href"><xsl:value-of select="Links/Content/Url"/></xsl:attribute>Stream</xsl:element></td>' >> "$XSL"
	echo '<td><xsl:element name="a"><xsl:attribute name="href"><xsl:value-of select="Links/TiVoVideoDetails/Url"/></xsl:attribute>Details</xsl:element></td>' >> "$XSL"
	# end XSL file
	echo '</tr></xsl:for-each></table></body></html></xsl:template></xsl:stylesheet>' >> "$XSL"
	# process XML via XSL into HTML
	/usr/local/bin/xml tr "$XSL" "$XML" >! "$OUT"
	# remove XSL & XML
	rm -f "$XSL" "$XML"
    endif
endif
set OUTSIZE = `wc -c $OUT | awk '{ print $1 }'`
if (-e "$OUT" && $OUTSIZE > 0) then
    # HTTP header
    echo "Content-Type: text/html"
    set AGE = `echo "$SECONDS - $DATE" | bc`
    echo "Age: $AGE"
    echo "Cache-Control: max-age=$TTL"
    echo -n "Last-Modified: "
    date -r "$DATE" '+%a, %d %b %Y %H:%M:%S %Z'
    echo ""
    cat "$OUT"
else if (-e "$OUT") then
    rm "$OUT"
else
    echo "Status: 202 Accepted"
    echo ""
endif
