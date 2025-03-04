#!/usr/bin/bash

# Send headers
echo "Content-Type: text/html"
echo
echo

# Send the content!
echo "<h1>Hello from CGI!</h1>"
echo "<hr>"
echo "<p>This is cool!</p>"
echo "<p>Generated at <code>$(date)</code></p>"
echo "<p>Script executed by <code>$(whoami)</code></p>"
