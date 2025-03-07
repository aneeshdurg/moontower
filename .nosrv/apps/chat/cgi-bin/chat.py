#!/usr/bin/python -u
# It's imperative that the shebang line above has -u for streaming events

import atexit
import json
import os
import select
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs

nosrv = Path("/home/aneesh/public/.nosrv/")
chat = nosrv / "apps/chat"
app = chat / "app.py"
db = chat / "chat.sqlite3"
interpreter = nosrv / "pydb/bin/python"


def kill_on_exit(p: subprocess.Popen):
    p.terminate()
    try:
        p.wait(timeout=1)
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()


def listener():
    """Stream new events to the client for 30s"""
    print("Content-Type: text/event-stream")
    print("X-Accel-Buffering: no")
    print("Cache-Control: no-cache")
    print("\n\n", end="")

    params = parse_qs(os.environ["QUERY_STRING"])
    since = "1970-01-01 00:00:00.00"
    if len(p := params.get("listen", [])) == 1:
        since = p[0]

    p = subprocess.Popen(
        ["inotifywait", "-m", db, "-e", "modify"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    atexit.register(lambda: kill_on_exit(p))
    assert p.stdout
    last_ts = since

    def heartbeat():
        print("data: heartbeat\n")

    def update():
        nonlocal last_ts
        sent_records = 0
        try:
            new_msgs = subprocess.check_output(
                [interpreter, app, "view", "--since", last_ts]
            ).decode()
            for msg in new_msgs.split("\n"):
                if len(msg.strip()):
                    j_msg = json.loads(msg)
                    last_ts = j_msg["timestamp"]
                    print(f"data: {msg}\n")
                    sent_records += 1
        except Exception as e:
            print("unexpected error", e)
            raise e
        return sent_records

    # Get all messages to start
    update()

    os.set_blocking(p.stdout.fileno(), False)
    fds = [p.stdout]
    while True:
        (r, _, e) = select.select(fds, [], fds, 1)
        if e:
            break
        if not r:
            # We got here via timeout
            heartbeat()
            continue

        should_update = p.stdout.readline()
        if not should_update:
            break
        # consume any other updates that we missed, so that we don't call
        # `update` multiple times without finding any new data to send
        while p.stdout.readline():
            pass
        if update() == 0:
            heartbeat()

    # Get new messages for every update
    while _ := p.stdout.readline():
        update()


def receiver():
    """Receive a new message from the client"""
    # Read at most 512KB - most messages will likely be less than 20KB even.
    message = sys.stdin.buffer.read(512 * 1024)
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
