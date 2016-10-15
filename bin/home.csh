#!/bin/csh
set API = "home"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set TTL = 15
set MAK = `cat ~$USER/.tivodecode_mak`
set TMP = "/Volumes/NITRO/TIVO"
if (! -e "$TMP") set TMP = "/tmp"
# get time
set SECONDS = `date "+%s"`
set DATE = `echo $SECONDS \/ $TTL \* $TTL | bc`

set MIXPANELJS = "http://$WWW/CGI/script/mixpanel.js"

# output set
set HTML = ( `echo "$TMP/tivo-$API.$DATE.html".*` )

# check HTML complete or in-progress for current interval
if ($#HTML < 1) then
    set HTML = "$TMP/tivo-$API.$DATE.html"
    echo "bin/$API -- Making $HTML" >>! $TMP/LOG
    # initial HTML file
    echo "<html>" >! "$HTML.$$"
    # temporary XML for containers
    set XML = "$TMP/tivo-$API.$$.xml"
    # get XML for all TiVos
    curl -s -o "$XML" "http://$WWW/CGI/tivo-allnowplaying.cgi"
    set XMLVAL = `( /usr/local/bin/xml val -q "$XML"; echo $status )`
    if ($XMLVAL == 0) then
	# XPATH
	set ITEM = "TiVoContainerList/TiVoContainer/Item"
	set LINKS = ( "$ITEM/Links/Content/Url" "ITEM/Links/TiVoVideoDetails/Url" )
	set XSL = "$TMP/tivo-$API.$$.xsl"

	# intiate XSL output file
	echo '<?xml version="1.0" encoding="UTF-8"?><xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">' >! "$XSL"
	echo '<xsl:template match="/"><html>' >> "$XSL"
	echo '<script type="text/javascript" src="'$MIXPANELJS'"></script><script>mixpanel.track('"'"tivo-$API"');</script>" >> "$XSL"
	echo '<title>Now Playing' >> "$XSL"
	# date -r "$DATE" >> "$XSL"
	echo '</title><body>' >> "$XSL"
	echo '<h2>Now Playing - ' >> "$XSL"
	date -r "$DATE" >> "$XSL"
	echo '</h2>' >> "$XSL"
	# set nowplaying
	echo '<div id="nowplaying"><input class="search" placeholder="Search"/>' >> "$XSL"
	echo '<button class="sort" data-sort="TiVoName">Sort by TiVoName</button>' >> "$XSL"
	echo '<button class="sort" data-sort="CaptureDate">Sort by CaptureDate</button>' >> "$XSL"
	echo '<button class="sort" data-sort="Title">Sort by Title</button>' >> "$XSL"
	# start table
	echo '<table border="1"><tr bgcolor="#9acd32">' >> "$XSL"

	# derive all DETAILS
	# set DETAILS = ( `/usr/local/bin/xml el -u "$XML" | egrep "$ITEM/Details/" | sed "s@.*/\([^/]*\)@\1@"` )
	# select pertinent details
	# set DETAILS = ( TiVoName Title EpisodeTitle EpisodeNumber CaptureDate ProgramId SeriesId SourceChannel SourceSize SourceStation )
	# set DETAILS = ( TiVoName SeriesId ProgramId Title EpisodeTitle EpisodeNumber SourceStation )
	set DETAILS = ( TiVoName CaptureDate HighDefinition SourceChannel Title EpisodeNumber EpisodeTitle Description )
	foreach i ( $DETAILS )
	    # output header element
	    echo "<th>$i</th>" >> "$XSL"
	end
	# add headers for Content & VideoDetails URLs
	echo "<th>Stream</th><th>VideoDetails</th><th>Link</th>" >> "$XSL"
	# complete header row
	echo '</tr>' >> "$XSL"

	# initiate table body
	echo '<tbody class="list">' >> "$XSL"
	# initiate for-select over Item Detail; set sort options
	echo '<xsl:for-each select="/TiVoContainerList/TiVoContainer/Item">' >> "$XSL"
	echo '<xsl:sort select="Details/CaptureDate" order="descending"/>' >> "$XSL"
	echo '<xsl:sort select="Details/Title"/>' >> "$XSL"
	echo '<xsl:sort select="Details/EpisodeTitle"/>' >> "$XSL"

	# iterate over all details
	echo '<tr>' >> "$XSL"
	foreach i ( $DETAILS )
	    echo $i | awk '{ OFS=""; printf "<td class=\"%s\"><xsl:value-of select=\"Details/%s\"/></td>\n", $1, $1 }' >> "$XSL"
	end
	# add Content and TiVoVideoDetails links
	echo '<td class="Stream"><xsl:element name="a"><xsl:attribute name="href"><xsl:value-of select="Links/Content/Url"/></xsl:attribute>Stream</xsl:element></td>' >> "$XSL"
	echo '<td class="Details"><xsl:element name="a"><xsl:attribute name="href"><xsl:value-of select="Links/TiVoVideoDetails/Url"/></xsl:attribute>Details</xsl:element></td>' >> "$XSL"
	echo '<td class="Show"><xsl:element name="a"><xsl:attribute name="href">http://'$WWW'/CGI/tivo-show.cgi?show=<xsl:value-of select="Details/Title"/></xsl:attribute>Show</xsl:element></td>' >> "$XSL"
	echo '</tr>' >> "$XSL"
	# end row processing
	echo '</xsl:for-each></tbody></table></div>' >> "$XSL"
	echo '<script src="http://cdnjs.cloudflare.com/ajax/libs/list.js/1.1.1/list.min.js"></script>' >> "$XSL"
	echo "<script>var options = { page: '5000', valueNames: [ 'Title', 'CaptureDate', 'TiVoName' ] }; var npList = new List('nowplaying', options);</script>" >> "$XSL"
	echo '</body></html></xsl:template></xsl:stylesheet>' >> "$XSL"
	# process XML via XSL into HTML
	/usr/local/bin/xml tr "$XSL" "$XML" >! "$HTML.$$"
	# remove XSL
	rm -f "$XSL" "$XML"
	# check output
	set HTMLSIZE = `wc -c "$HTML.$$" | awk '{ print $1 }'`
	if ($HTMLSIZE == 0) then
	    rm -f "$HTML.$$"
	    set ERROR = "Invalid transformation"
	else
	    mv -f "$HTML.$$" "$HTML"
	    echo "bin/$API -- $HTML -- SUCCESS" >>! $TMP/LOG
	endif
    else
	rm -f "$XML"
    endif
else
    echo "bin/$API -- In-process $HTML" >>! $TMP/LOG
endif

if ($?ERROR) then
    echo "bin/$API -- $HTML -- $ERROR" >>! $TMP/LOG
    rm -f "$HTML".*
endif
