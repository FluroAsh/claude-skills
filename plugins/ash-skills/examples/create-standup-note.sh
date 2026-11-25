#!/bin/sh
# Usage: create-standup-note.sh [folder] [template] [YYYY-MM-DD]
# Or set STANDUP_FOLDER, STANDUP_TEMPLATE and STANDUP_DATE. Date defaults to today.
set -eu

folder=${1:-${STANDUP_FOLDER:-}}
template=${2:-${STANDUP_TEMPLATE:-}}
day=${3:-${STANDUP_DATE:-$(date +%Y-%m-%d)}}

if [ -z "$folder" ] || [ -z "$template" ]; then
  echo "usage: $0 <standup folder> <template file> [YYYY-MM-DD]" >&2
  exit 2
fi

# BSD (macOS) and GNU date parse dates differently.
fmt() {
  date -j -f %Y-%m-%d "$day" "+$1" 2>/dev/null || date -d "$day" "+$1"
}

case $(fmt %u) in 6|7) exit 0 ;; esac

dir="$folder/$(fmt %Y)/$(fmt '%m - %B')"
note="$dir/$(fmt %m-%d-%y).md"
[ -e "$note" ] && exit 0

mkdir -p "$dir"
# noclobber makes the create atomic, so a note made between the check and here is never overwritten.
(set -C; cat "$template" > "$note") 2>/dev/null || exit 0
echo "created $note"
