#!/usr/bin/bash

echo -e "Content-Type: text/plain\n\n"

# TODO: support multiple pages here via query param
~/accesscounter/bin/python ~/accesscounter/accesscounter.py touch index
