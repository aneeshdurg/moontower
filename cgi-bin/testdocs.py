#!/usr/bin/python
import os
from pathlib import Path

# Send headers
print("Content-Type: text/html\n\n")

# Send content
includes_root = Path("/home/aneesh/public/includes/")

print("""\
<!DOCTYPE html>
<html>
  <head>
    <link rel="stylesheet" href="/~aneesh/test/style.css"/>
    <title>docs</title>
  </head>
  <body>
    <div class="container">
""")

with open(includes_root / "header.html") as f:
    print(f.read())

docs_root = includes_root / "docs/build"
for doc in sorted(os.listdir(docs_root)):
    inc = docs_root / doc
    with inc.open() as f:
        print(f.read())
    print("<hr>")

print("""\
    </div>
  </body>
</html>
""")
