#!/usr/bin/bash

# Send headers
echo -e "Content-Type: text/html\n\n"

# Send the content!
echo "\
<!DOCTYPE html>
<html>
<head>
  <link rel=\"stylesheet\" href=\"/~aneesh/test/style.css\">
  <title>MTCC</title>
</head>

<body>
<div class=\"container\">
"

echo "  <div class=\"header\">"
cat /home/aneesh/public/includes/header.html
cat /home/aneesh/public/includes/description.html
echo "  </div>"

echo "\
  <br>
  <br>
  <div class=\"userbar\">
    <h2>Users:</h2>
    <ul>"
for dir in $(find /home -maxdepth 1 -type d | grep -v '^/home/root$\|^\/home$'); do
  user=$(basename "$dir")
  echo "      <li><a href=\"/~${user}\">~/${user}</a></li>"
done
echo "\
      </ul>
  </div>"

cat /home/aneesh/public/includes/ethos.html

echo "\
  <div class=\"footer\">
    <br>
    <footer>
      <i>Generated on <span class=\"generateddate\">$(date)</span></i>
    </footer>
  </div>
</div>
</body>
</html>"
