#!/bin/csh
set API = "copyProtected"
set WWW = "www.dcmartin.com"
set LAN = "192.168.1"
set MAK = `cat ~$USER/.tivodecode_mak`
# 90 days 
set TTL = `echo "60 * 60 * 24 * 90" | bc`
set TMP = "/Volumes/RAID10/TIVO"
if (! -e "$TMP") set TMP = "/tmp"
# get time
set SECONDS = `date "+%s"`
set DATE = `echo $SECONDS \/ $TTL \* $TTL | bc`

if ($?QUERY_STRING != 0) then
    set TIVO = `echo $QUERY_STRING | sed "s/.*port=\(..\).*/\1/"`
    if ($TIVO < 20 || $TIVO > 24) unset TIVO
    set ID = `echo $QUERY_STRING | sed "s/.*id=\([0-9]*\).*/\1/"`
endif

if ($?TIVO == 0 || $?ID == 0) then
    set ERROR = "INVALID"
    goto done
else
    set ERROR = "false"
endif
 
    # get metadata
    set CSV = "$TMP/tivo-$API.$TIVO.$$.csv"
    curl -s -o "$CSV" "http://$WWW/CGI/tivo-csv.cgi?port=$TIVO"
    set CSVSIZ = `ls -l "$CSV" | awk '{ print $5 }'`
    if ($CSVSIZ == 0) then
        set ERROR = "no data"
	goto done
    endif
    set COLS = ( `head -1 "$CSV" | sed "s/,/ /g"` )
    set j = 1
    foreach i ( $COLS )
	if ( $i == "CopyProtected" ) then
	    set copypro = $j
	endif
	set j = `echo "$j + 1" | bc`
    end
    # subselect show
    egrep "$ID" "$CSV" >! "$CSV.$$" ; mv -f "$CSV.$$" "$CSV"
    set CSVSIZ = `ls -l "$CSV" | awk '{ print $5 }'`
    if ($CSVSIZ == 0) then
        set ERROR = "not found"
	goto done
    endif
    if ($?copypro) then
        set COPYPRO = `cut -d , -f $copypro "$CSV" | sed 's/"//g'`
	if ($COPYPRO == "Yes") then
	    set ERROR = "true"
	endif
    endif
    rm "$CSV"

done:

if ($?ERROR) then
    echo "Content-Type: text/text"
    echo ""
    echo "$ERROR"
endif
