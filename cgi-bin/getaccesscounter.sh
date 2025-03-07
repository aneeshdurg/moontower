#!/usr/bin/bash

# GET'ing /~aneesh/cgi-bin/getaccesscounter.sh?<service> will update the access
# counter for service. Note that the table for the service must be created first
# by doing:
#   cd ~/public/.nosrv/accesscounter
#   ./bin/python ./accesscounter.py add <service>
# If no query param is supplied then the default service is "index"

echo -e "Content-Type: text/plain\n\n"

ROOT=~/public/.nosrv/accesscounter

SERVICE=${QUERY_STRING:-index}
if [-z "$SERVICE"]; then
  SERVICE="index"
fi

$ROOT/accesscounter.py touch $SERVICE
