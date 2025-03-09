title: Building a CGI-powered app on moontowercomputing.club!

---

In the past week I've learned about CGI and generally how web servers work. I've
put that knowledge together into a pretty cool [webapp](/~aneesh/chat) and along
the way I've found some "best practices" that I think is worth sharing!

---

## Motivation/Pictochat

When I was a nerdy middle schooler, I used to sneak my DS to school. During
classes, I'd talk to my other sneaky friends with pictochat! It was such a fun
and thrilling experience, and I've never really felt that excitement with any
other chat platform. I figured that building an app similar to pictochat would
be a great way to stress test the CGI server and iron out any kinks. And there
were many kinks indeed - mostly around process management and caching/streaming,
but maybe that's for a separate blog post! However, I'm now pretty confident
that other users on `moontowercomputer.club` are able to build anything they
want with CGI, and I think I also made a fun little toy to boot!

## What is CGI?

Common Gateway Interface is a family of protocols for webservers to communciate
with arbitrary applications to service HTTP requests - basically, instead of
serving a static file for a request, or routing to a full-fledged HTTP server,
we can have small, individual scripts/programs that run when an end point is
accessed. For example, if you go to
`https://moontowercomputer.club/~USER/cgi-bin/foo.sh`, instead of giving you the
contents of the file `/home/USER/public/cgi-bin/foo.sh`, `foo.sh` is executed
and the output is sent to the browser. It is assumed that `foo.sh` will output a
stream where any HTTP headers are sent (e.g. `Content-Type: text/html`) followed
by two blank lines, and then the remainder of the stream is passed along to the
browser directly (notably, it isn't assumed that the stream contents are ASCII
after the headers - allowing scripts to send back images/media, or any binary
data).

On `moontowercomputer.club` CGI scripts receive a number of variables in the
environment, including any query parameters (`$QUERY_STRING`) and for `POST/PUT`
requests, the request body can be read from STDIN, allowing programs to fully
implement a sort of ad-hoc server. If you've ever worked with "serverless"
applications before, this is vaguely similar.

## App Architecture

The app is relatively straightfoward. Broadly, there are three main operations
we need to implement in the backend:

1. Take in new messages and save them to a database
2. Provide a stream of new messages being added to the database to send to the
  frontend
3. Delete old messages

For `1` - we can have a POST endpoint that consumes a messages and saves it to a
sqlite file. For `2` - we can use `inotify` events to detect updates to the
database and use an event stream to send new events back to the frontend. And
finally for `3`, a simple GET endpoint that triggers a script to delete rows
from the database will suffice.

This isn't the best architecture and there's so many ways it can be made better.
But the point of this project wasn't the build the best pictochat clone, it was
just to build a pictochat clone that would let me find out if everything in the
CGI path worked.

The most interesting part of this was figuring out how to get `2` to work. I
learned about `Content-Type: text/event-stream`, which is used for streaming
text to a client. On the javascript side, this can be connected to with an
`EventStream`, as long as your data is in the form `data: {data}\n\n` for
each message. I realized that there could be instances where the connection
drops, so I added an additional query parameter on the endpoint so the client
can provide a timestamp to indicate that they only want to subscribe to
notifications newer than some known timestamp. This is needed because when a new
client connects, the default behavior is to send all currently known messages to
the client before waiting for new events.

It's also important to note that when working with streams, it's probably best
to also sent the header `X-Accel-Buffering: no` and `Cache-Control: no-cache` to
disable caching (in `nginx` and the browser respectively) and ensure timely and
reliable delivery of messages.

Additionally, you also need to send some kind of heartbeat to prevent the
connection from being closed.

Putting it all together, the CGI side of my app can be found at <https://github.com/aneeshdurg/moontower/blob/main/.nosrv/apps/chat/cgi-bin/chat.py>

### Process Management

If you look at the code you may wonder how processes are managed in the event of
things like client disconnects when listening to a stream. Essentially, the CGI
server detects that the connection is closed, sends a `SIGTERM` to the CGI
script, waits for a little while, then sends a `SIGKILL` if the process is still
alive. For my application, this terminates the CGI script, but leaves zombie
processes for any children I spawned. To get around that I added a bit of code:

```python
def kill_on_exit(p: subprocess.Popen):
    p.terminate()
    try:
        p.wait(timeout=1)
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()


# This is the method that services the streaming request
def listener():
    print("Content-Type: text/event-stream")
    print("X-Accel-Buffering: no")
    print("Cache-Control: no-cache")
    print("\n\n", end="")
    ...

    p = subprocess.Popen(
        ["inotifywait", "-m", db, "-e", "modify"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    atexit.register(lambda: kill_on_exit(p))

```

The `atexit` callback will now ensure that my child process is cleaned up
correctly when the client disconnects.

## File structure

Serving files can be daunting - especially when you want to ensure that you
don't accidentally make you database downloadable. While I could keep my app,
the database, and any resources that don't need to be served outside of the
`~/public` directory, it makes development and deployment messy. To combat that,
I found a nice method that I wanted to share with everyone.

Here is a simplified view of what my `~/public` directory looks like:

```
.
├── .git
│   └── ...
├── .nosrv
│   ├── .gitignore
│   ├── apps
│   │   ├── ...
│   │   └── chat
│   │       ├── app.py
│   │       ├── cgi-bin
│   │       │   └── chat.py
│   │       ├── chat.sqlite3
│   │       └── static
│   │           ├── index.html
│   │           ├── script.js
│   │           └── style.css
│   ├── pydb
│   │   └── ...
│   └── setupvenv.sh
├── cgi-bin
│   ├── ...
│   └── chat -> ../.nosrv/apps/chat/cgi-bin/
├── chat -> .nosrv/apps/chat/static/
└── index.html
```

My entire `~/public` directory is a git repo (which you can see publicly at
<https://github.com/aneeshdurg/moontower>). The `nginx` config is set to _never_
serve any hidden files or directories, so things in `.git` and `.nosrv` are not
publicly accessible via <https://moontowercomputer.com/>. This means that I can
keep things like my database inside `.nosrv` without the possibility of users
downloading the entire database. To make something visible publicly, I
[symlink](https://en.wikipedia.org/wiki/Symbolic_link) it into somewhere in
`~/public`.

The scripts that manage the database all run inside of a
[venv](https://docs.python.org/3/library/venv.html) to make dependency
management easy. I've documented the command I used to create the venv
[here](https://github.com/aneeshdurg/moontower/blob/main/.nosrv/setupvenv.sh).
The CGI script itself just uses the system python since it spawns a subprocess
that calls my database scripts, but I could have used the `venv` interpreter by
pointing to it in the shebang line. In a way, my current approach naturally
led me to rediscover the
[MVC](https://developer.mozilla.org/en-US/docs/Glossary/MVC) pattern and gain a
greater appreciation for it.

This system has been working for me pretty well. I now have three different
"services" in `.nosrv/apps`, and organizing files and resources for each
"service" has been pretty easy and self-documenting with the symlinks!

# Conclusion

I think before I started on this journey, I would have felt like building an
app like this was best done by spinning up a webserver like `flask` and hosting
on the free tier of some cloud provider like AWS. However, I think
`nginx+cgi+self-hosting` is an underrated approach for building fun weekend
projects and making cool things to share with the world around us. CGI scripts
are awesomely powerful as they let users build complex services without needing
to reserve ports, manage long-lived server processes, or modify the global
webserver config. I definitely learned a lot - during my debugging sessions when
the CGI stuff wasn't working, I even ended up cloning and modify the nginx
source code to better understand how the fastcgi model works lol! Hopefully this
post helps/inspires others to build as well. Happy Hacking!
