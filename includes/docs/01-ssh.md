## SSH Access

### What is SSH?

<b>S</b>ecure <b>SH</b>ell (or `SSH`), is a protocol for remote accessing a
computer via a secure, encrypted connection. If you're on windows, you may need
to download an SSH client, such as [PuTTY](https://www.putty.org/), or you can
access the `ssh` command through
[WSL](https://learn.microsoft.com/en-us/windows/wsl/install).

On MacOS/Linux, the `ssh` command should already be available in your terminal.

To login, you'll need to SSH to the host `moontowercomputer.club`. However
`moontowercomputer.club` has disabled password based access, so you'll need to
send us your public key to use key based authentication.

<details>
<summary>Click me to learn more about key based authentication</summary>
I won't bore you with all the gory mathematical details, but basically a
public/private key pair is sort of like a lock and key. Your public key is the
"lock", and you can share it far and wide. Your private key is the
"key" to the public key's "lock", and should *never* be shared. Like *never*
*never*. `SSH` uses the public key to encrypt your connection/data, and this
encrypted information can *only* be decrypted by your private key - you use your
"key" (private key) to open the "lock" (public key).
</details>

### How do I generate a public/private key pair?

On windows you may need to follow [these
steps](https://www.ssh.com/academy/ssh/putty/windows/puttygen). I'm not a
windows user so I haven't tried it personally. Please let me know if they
do/don't work and I'll update this guide accordingly (and help you get things
set up if it didn't work).

On MacOS/Linux, it's very straightforward:

```bash
# Generate the key
ssh-keygen -t rsa
# Accept all the default in the command above, or customize them. The prompt is
# relatively straightforward, the only thing you might care about it is
# protecting the files with a password.
# Next, display the contents of the public key. You'll want to send me the
# output of this command so that I can grant you access to server.
cat ~/.ssh/id_rsa.pub
```

### I'd like to use multiple machines to log in to moontower, how can I do that?

Just paste additional public keys in `~/.ssh/authorized_keys`, one public key
per line! While you _can_ copy around your public/private key to every
machine you'd like to log in from, this is a *bad* idea because it's a
security risk. Just generate a new key pair for each machine.

### I've logged in, but all I see is a terminal. This is scary.

Anything is daunting when you do it for the first time, but this is just like
riding a bike! Eventually, it'll feel super natural, but at first you will
struggle as you learn. Here's a good guide to get you started: <https://www.freecodecamp.org/news/linux-command-line-bash-tutorial/>.

Please, please, please ask questions on our group chat. We've got a lot of
people who _love_ to share their interests and bring new people into our
community. We strive to be an inclusive, accessible, and beginner friendly
space, and if we don't uphold those standards, or could serve your learning
journey better, please let us know so we can learn and grow together.

### Other resources

Here's some things to google as you learn about `SSH`!

+ `ssh-copy-id` - copies public keys to an SSH server (not super useful for us,
  because it requires password authentication initially, but good to know about)
+ `scp` - copy a file from your local computer to a remote server via `ssh`
+ `mosh` - a newer utility that beefs up what `ssh` can do. We haven't enabled
  this on `moontower` yet though.
+ `ssh-fs`
+ vscode's ssh plugins
+ X-forwarding - lets you run graphical applications over SSH
+ `~/.ssh/config` - your SSH configuration file. You can set custom aliases for
  SSH hosts among other things.
