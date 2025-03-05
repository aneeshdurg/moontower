#!/usr/bin/python
import subprocess
# Send header
print("Content-Type: text/html")
print("\n\n", end="")

date = subprocess.check_output(['date']).decode().strip()
whoami = subprocess.check_output(['whoami']).decode().strip()

print(f"""\
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="/~aneesh/static/style.css">
        <title>CGI test</title>
    </head>
    <body>
    <div class="container">
        <h1>Hello from CGI!</h1>
        <hr>
        <p>This is cool!</p>
        <p>Generated at <code>{date}</code></p>
        <p>Script executed by <code>{whoami}</code></p>
    </div>
    </body>
</html>
""")


