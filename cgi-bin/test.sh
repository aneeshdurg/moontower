#!/usr/bin/bash

# Send headers
echo "Content-Type: text/html"
echo
echo

# Send the content!
echo "<!DOCTYPE html>"
echo "<html>"
echo "<head>"
echo "  <link rel=\"stylesheet\" href=\"style.css\">"
echo "  <title>MTCC</title>"
echo "</head>"

echo "<body>"
echo "<div class=\"container\">"

cat /home/root/public/includes/header.html

cat /home/root/public/includes/ethos.html

echo "<h2>Users:</h2>"
echo "<ul>"
for dir in $(find /home -maxdepth 1 -type d | grep -v '^/home/root$\|^\/home$'); do
  user=$(basename "$dir")
  echo "  <li><a href=\"/~${user}\">~/${user}</a></li>"
done
echo "</ul>"

echo "<footer>"
echo "  <i>Generated on <span class=\"generateddate\">$(date)</span></i>"
echo "</footer>"

echo "</div>"
echo "</body>"
echo "</html>"
