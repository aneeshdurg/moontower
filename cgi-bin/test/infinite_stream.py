#!/usr/bin/python -u
from time import sleep, time

print("Content-Type: text/event-stream")
print("X-Accel-Buffering: no")
print("\n\n", end="")

while True:
    print(time())
    sleep(1)
