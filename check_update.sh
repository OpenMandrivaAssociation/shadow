#!/bin/sh
# Multiple version scheme changes... We have to enforce the
# latest (4.13 > v4.12 > 20001016)
git ls-remote --tags https://github.com/shadow-maint/shadow.git 2>/dev/null|awk '{ print $2; }' |sed -e 's,refs/tags/,,;s,^v,,' |grep -E '^[0-9.]+$' |grep -v '^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$' |sort -V |tail -n1
