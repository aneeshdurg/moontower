#!/usr/bin/bash

echo -e "Content-Type: text/plain\n\n"

ROOT=~/public/.nosrv/accesscounter

# TODO: support multiple pages here via query param
$ROOT/bin/python $ROOT/accesscounter.py touch index
