#!/usr/bin/python
import sys

print("Status: 200 OK\n\n")

with open("/home/aneesh/tmp/result.txt", 'ab') as f:
    f.write(sys.stdin.buffer.read())
