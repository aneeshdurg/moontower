## Using Rust

Hello rustaceans! Rust is awesome, but takes up so much space. So we're going to
share, and we're going to use a system-wide install of rust. It's present at
`/opt/rust`.

Here's a snippet from my [fish](https://fishshell.com/) config that I use to
access rust tools, you'll have to figure out the equivalent for your shell.

```bash
source "/opt/rust/env.fish"
set -x RUSTUP_HOME=/opt/rust
```

Note that you'll still have `~/.cargo` for anything you build or install
yourself, the only thing that's shared is the rust toolchain. If you decide that
you're not a morally upright person who is okay with really eating up our shared
disk space (or if you just need a specific or non-stable toolchain version) ,
you can always unset `RUSTUP_HOME`, run `rustup default stable` (or whatever
version/tag of rust you want), and it'll install it to your home directory. I'd
recommend that you build elsewhere and cross compile though - the compute
resources on `moontower` are also pretty limited, so it's really not a great
development experience. Rust isn't necessarily installed here to facilitate
development so much as just providing access to utilities installable through
`cargo`.
