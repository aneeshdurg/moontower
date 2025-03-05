#!/usr/bin/python
import os

print("Content-Type: text/plain\n\n")
for k, v in os.environ.items():
    print(f"{k}={v}")

print(f"query str = {os.environ['QUERY_STRING']}")
