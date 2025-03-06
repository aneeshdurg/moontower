#!/usr/bin/python -u
import base64
import json
import os
import subprocess
import sys
from multiprocessing import Process
from pathlib import Path
from urllib.parse import parse_qs

nosrv = Path("/home/aneesh/public/.nosrv/")
chat = nosrv / "apps/chat"
app = chat / "app.py"
db = chat / "chat.sqlite3"
interpreter = nosrv / "pydb/bin/python"


def _listener(since: str):
    """Stream new events to the client for 30s"""

    # TODO - is this timeout necessary?
    p = subprocess.Popen(
        ["timeout", "30", "inotifywait", "-m", db, "-e", "modify"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    last_ts = since

    def update():
        nonlocal last_ts
        try:
            new_msgs = subprocess.check_output(
                [interpreter, app, "view", "--since", last_ts]
            ).decode()
            for msg in new_msgs.split("\n"):
                if len(msg.strip()):
                    j_msg = json.loads(msg)
                    last_ts = j_msg["timestamp"]
                    print(f"data: {msg}\n")
        except Exception as e:
            print("unexpected error", e)
            raise e

    # Get all messages to start
    update()
    # Get new messages for every update
    while _ := p.stdout.readline():
        update()


def listener():
    print("Content-Type: text/event-stream")
    print("X-Accel-Buffering: no")
    print("Cache-Control: no-cache")
    print("\n\n", end="")

    params = parse_qs(os.environ["QUERY_STRING"])
    since = "1970-01-01 00:00:00.00"
    if len(p := params.get("listen", [])) == 1:
        since = p[0]

    p = Process(target=_listener, args=(since,))
    p.start()
    p.join(timeout=30)
    p.terminate()
    p.join()


def receiver():
    """Receive a new message from the client"""
    # Consume all of the input
    # TODO - limit the maximum size here
    message = sys.stdin.buffer.read()
    # TODO - parse the message
    try:
        p = subprocess.Popen(
            [interpreter, app, "message"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        p.communicate(message)
        assert p.returncode == 0
        print("Status: 200 OK\n\n")
    except Exception as e:
        print("Status: 500 ERR")
        print("Content-Type: text/plain")
        print("\n\n", end="")
        print("Internal Error:\n")
        print(e)


def prune():
    """Delete stale messages"""
    try:
        subprocess.check_call([interpreter, app, "prune"])
        print("Status: 200 OK\n\n")
    except Exception as e:
        print("Status: 500 ERR")
        print("Content-Type: text/plain")
        print("\n\n", end="")
        print("Internal Error:\n")
        print(e)


query = os.environ.get("QUERY_STRING", "")
if query.startswith("listen"):
    listener()
elif query == "send":
    receiver()
elif query == "prune":
    prune()
else:
    print("Status: 500 ERR")
    print("Content-Type: text/plain")
    print("\n\n", end="")
    print("Error: Invalid URI")
