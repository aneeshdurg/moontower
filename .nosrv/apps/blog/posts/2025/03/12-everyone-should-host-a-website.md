title: Everyone Should Host a Website

---

I've been thinking a lot about self-hosting websites recently and wanted to put
down some of my thoughts.

---

Recently I setup the server for <https://moontowercomputer.club> and it was a
lot of fun. I've been having a blast setting up my new homepage over at
<https://moontowercomputer.club/~aneesh> and even wrote a little static site
generator to build this blog along with some [CGI shenanigans](../7/07-moontower-cgi.html).
Along the way I started thinking about the current state of the internet.

Currently, we have more people online than every before in history. But
vanishingly few people have self-hosted personal websites. Most people are
content with their social media profiles on popular websites, a few people use
platforms like medium/substack/etc, and a majority of the remaining netizens
seem to use hosted services like github pages. I'm no exception to this rule.
My main website (<https://aneeshdurg.me>) is hosted on github pages, and has
been for almost a decade. To be clear, I think there's nothing wrong with that,
and it's a very attractive options to new developers for a reason (regardless of
any misgivings I may or may not have about github as a platform, they've
definitely helped a lot of people start their journeys in tech). To me this
phenomenon of having billions of people online, but only within a few
concentrated spaces seems problematic. Large scale social media platforms have
been shown to have had some real adverse effects on society. Extremism is [on
the
rise](https://www.gao.gov/blog/online-extremism-growing-problem-whats-being-done-about-it),
vulnerable members of society (such as children/teenagers) are faced with
[threats to their mental
health](https://health.ucdavis.edu/blog/cultivating-health/social-medias-impact-our-mental-health-and-tips-to-use-it-safely/2024/05),
and anecdotally, I've heard people from all walks of life, and of all political
affiliations complain about how the feel mistrustful
of the "algorithms" showing them content at this point.

Self-hosting websites is no panacea to all of the world's problems, but there's
definitely some real positives. For example, with more individuals self-hosting,
a greater portion of netizens would understand how the internet operates and
would be better equipped to identify and protect themselves against
cyberthreats. I also think that having more people online would help prevent
against a monoculture on the internet (but only to some extent - I think most
people would probably use the same or similar stacks). A greater portion of the
internet could be free of tracking/advertising. A world where everyone
self-hosts their personal web presence is also a world where people have greater
control over data that they make available online.

Now to be fair, there's also some very real downsides. There's economies of
scale that would be foregone, issues with moderation, questions raised about
security and safety, and concerns about availability/reliability that may
adversely impact [certain communities over
others](https://en.wikipedia.org/wiki/Digital_divide). But in my opinion many of
these are problems would be solved if there was greater consumer demand. Many of
these challenges aren't technically that intense. For example, there's already
docker images that pre-package reverse proxies like `nginx` or `apache`, and
provide a default configuration that most people could just use as-is for a very
simple setup. Other setup steps like `HTTPS` and setting up dynamic DNS is also
technically trivial (at least when working with major domain name registries).
It's not too hard to imagine a relatively locked down operating system with all
these tools preinstalled and set to safe defaults being sold to non-technical
consumers who can then plug it into their home network and be online. In terms
of setting things up on the home network side, my ISP already makes this super
easy in my router's configuration page by having a dropdown menu to select the
service I want to expose with preexisting selections for `HTTP` and `HTTPS`
along with most other popular protocols (e.g. `SSH`). I'm convinced that the
technical hurdles of self-hosting are at this point are a mere formality. It is
work that needs to be done carefully, but tech-fu does not need to be a barrier
for hosting your own webpage. 

The only problem that isn't easily solved with self-hosting is moderating
hateful/harmful content. I'm not really sure what a good solution to that is
personally, but I don't think existing social media platforms handle that super
well to begin with. There's definitely still some avenues for moderation, like
pressuring a domain registry to drop a client, and relying on the laws and
regulations of your place of residence (though in many cases that may not be a
viable option). I do still think that overall a more decentralized model of the
internet where people build their own personal pages does more good than harm
by combating the adverse effects of social media biasing towards extreme
viewpoints, but this is something I need to learn more about.

## What can we do to lower the barriers of entry?

I don't know of any real good solutions, but here's some unstructured thoughts
I've had about ways to get more people participating with self-hosted websites.

+ Start more Computer Clubs!
+ Do work in the open - share the work that you do on blogs and other places to
  make it easier to find content about how to get started with these things. In
  the current day and age there's also the very real chance that an AI is
  reading and regurgitating your content. That sucks, but if a non-technical
  person learns how to do something cool because an AI learned fro my writing
  and then vomited it back at someone else, I'll still call it a win.
+ Promote the services that help make this more accessible (let's encrypt, ddns)
+ Raise computer literacy - allow more people to take control of the tech in
  their lives and feel more capable.
+ Advocate for free software
+ Build products that help bring in newcomers
+ Strengthen the social graph of the internet - share links not likes,
  participate in webrings.

## How to get involved

I think it's often hard for people to get involved in something that sounds cool
because it's not obvious what the first steps are. I hope that the rest of this
post helps clarify that a bit!

### How do websites actually work?

It's probably good to quickly sketch out what happens when you visit a website.
When you go to the URL `https://moontowercomputer.club`, your webbrowser makes
an `HTTPS` request. But before it can do that, it needs to know where in the
internet `moontowercomputer.club` is - sort of like how before you can call a
business you need to know their phone number. Just knowing the name isn't
enough. Fortunately, just like how we can look up phone numbers, computers can
lookup IP addresses for a domain name (a domain name is what we'd call the
`moontower.club` part of the URL). Once you know where to look, your browser can
proceed with the HTTP request. On systems with [curl]() installed, we can take a
closer look at what this process looks like. Lines starting with "#" are added
by me as annotations.

```console
aneesh@moontower:~$ curl -vvv https://moontowercomputer.club/~aneesh

# The "resolved" here means that it's found the IP for moontowercomputer.club
# Note that :443 - that's the "port" for HTTPS

* Host moontowercomputer.club:443 was resolved.
* IPv6: (none)

# You can see the IP address that curl found here:

* IPv4: 70.234.252.188
*   Trying 70.234.252.188:443...
* Connected to moontowercomputer.club (70.234.252.188) port 443

# These details are related to the HTTPS protocol, it's a bit out of scope for
# this post, but briefly, it allows the data to be encrypted while it's being
# sent over

* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
*  CAfile: /etc/ssl/certs/ca-certificates.crt
*  CApath: /etc/ssl/certs
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / X25519 / id-ecPublicKey
* ALPN: server accepted http/1.1
* Server certificate:
*  subject: CN=moontowercomputer.club
*  start date: Mar  4 03:38:07 2025 GMT
*  expire date: Jun  2 03:38:06 2025 GMT
*  subjectAltName: host "moontowercomputer.club" matched cert's "moontowercomputer.club"
*  issuer: C=US; O=Let's Encrypt; CN=E5
*  SSL certificate verify ok.
*   Certificate level 0: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA384
*   Certificate level 1: Public key type EC/secp384r1 (384/192 Bits/secBits), signed using sha256WithRSAEncryption
*   Certificate level 2: Public key type RSA (4096/152 Bits/secBits), signed using sha256WithRSAEncryption
* using HTTP/1.x

# We're getting a response from `moontowercomputer.club`!!!

> GET /~aneesh/ HTTP/1.1
> Host: moontowercomputer.club
> User-Agent: curl/8.5.0
> Accept: */*
>
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* old SSL session ID is stale, removing
< HTTP/1.1 200 OK
< Server: nginx/1.22.1
< Date: Wed, 12 Mar 2025 20:42:08 GMT
< Content-Type: text/html
< Content-Length: 3484
< Last-Modified: Mon, 10 Mar 2025 04:07:17 GMT
< Connection: keep-alive
< ETag: "67ce6575-d9c"
< Accept-Ranges: bytes
<

# Everything after this is the raw HTML that your browser renders into my
# homepage!

...
```

### How do you host one at home?

I recently came across this really good guide for setting up a website off of a
raspberry pi at home! <https://mirawelner.com/posts/website_howto.html>

Moontower Computer Club's hosting solution is pretty similar except I set up my
pi to use nginx. I kinda wish I had tried apache instead though because I had a
few issues getting things like CGI to work the way I wanted.

You don't specifically need a raspberry pi, any old computer will do. I
recommend installing linux on it (or at least running a linux VM) to make things
a bit easier for yourself.
