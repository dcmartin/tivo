#!/bin/bash

usage() { echo "Usage: $0 [-o <MPG>] [-u <URL>] [ -x <STATUS> ]" 1>&2; exit 1; }

while getopts ":m::o:u:x:" i; do
    case "${i}" in
        m)
            m=${OPTARG}
            ;;
        o)
            o=${OPTARG}
            ;;
        x)
            x=${OPTARG}
            ;;
        u)
            u=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${m}" ] || [ -z "${o}" ] || [ -z "${u}" ] || [ -z "${x}" ]; then
    usage
fi

    exec 0>&- # close stdin
    exec 1>&- # close stdout
    exec 2>&- # close stderr
    ( curl -s --cookie "sid=abc" -k --anyauth -u tivo:"${m}" "${u}" | /usr/local/bin/tivodecode - -m "${m}" -o "${x}" ; mv -f "${x}" "${o}" ) &
