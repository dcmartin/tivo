#!/bin/csh
set API = "allcsv"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set TTL = 900
set TMP = "/Volumes/RAID10/TIVO"
set MAK = `cat ~$USER/.tivodecode_mak`
if (! -e "$TMP") set TMP = "/tmp"
# get time
set SECONDS = `date "+%s"`
set DATE = `echo $SECONDS \/ $TTL \* $TTL | bc`

# HTTP header
echo "Content-type: text/csv"
set AGE = `echo "$SECONDS - $DATE" | bc`
echo "Age: $AGE"
echo "Cache-Control: max-age=$TTL"
echo -n "Last-Modified: "
date -r "$DATE"
echo ""

# what we're building / looking to dump
set CSV = "$TMP/tivo-all.$DATE.csv"
# test for cache
if (! -e "$CSV") then
    # remove old caches
    rm -f $TMP/tivo-all.*.csv
    # temporary XML for containers
    set XML = "$CSV:r.$$.xml"
    curl -s -o "$XML" "http://$WWW/CGI/tivo-allnowplaying.cgi"
    if (-e "$XML") then
	set TOTALELEMS = ( `/usr/local/bin/xml sel -t -v "/TiVoContainerList/Details/TotalItems" "$XML"` )
	set BASE = "TiVoContainerList/TiVoContainer/Item/Details"
	set ELEM = ( `/usr/local/bin/xml el -u "$XML" | egrep "$BASE/" | sed "s@.*/\([^/]*\)@\1@"` )
	mkdir $TMP/$$
	foreach i ( $ELEM )
	    /usr/local/bin/xml sel -t -v "/$BASE/$i" "$XML" | sed 's/,/\&#44;/g' | sed 's/"/\&quot;/g' | sed 's/^\(.*\)/"\1"/' >! "$TMP/$$/$i"
	end
	# Get URL for Content and VideoDetails
	set URLS = ( "Content" "TiVoVideoDetails" )
	foreach URL ( $URLS )
	    /usr/local/bin/xml sel -t -v "TiVoContainerList/TiVoContainer/Item/Links/$URL/Url" "$XML" >! "$TMP/$$/$URL"
	end
	# add to ELEM
	set ELEM = ( $URLS $ELEM )
	echo "$ELEM" | sed "s/ /,/g" >! "$CSV"
	( cd $TMP/$$ ; paste -d "," $ELEM ) >> "$CSV"
	rm -fr TMP/$$
    endif
    rm -f "$XML"
endif
cat "$CSV"
echo ""
