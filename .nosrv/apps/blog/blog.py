import argparse
import os
import select
import subprocess
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


SEPERATOR = "---"


@dataclass
class Post:
    mtime: float
    headers: dict[str, str]
    preview: str
    body: str
    year: int
    month: int
    day: int
    name: str
    is_draft: bool
    cached: bool

    @classmethod
    def from_file(cls, gen: "Generator", filepath: Path):
        month_dir = filepath.parent
        month = int(month_dir.stem)
        year_dir = month_dir.parent
        year = int(year_dir.stem)
        name = filepath.stem
        is_draft = name.startswith("draft.")
        if is_draft:
            day = int(name.split(".")[1].split("-")[0])
        else:
            day = int(name.split("-")[0])

        headers = {}

        mtime = filepath.lstat().st_mtime
        cache_key = urllib.parse.quote_plus(str(filepath))
        with filepath.open() as f:
            cached = True
            while (line := f.readline().strip()) != SEPERATOR:
                if not line:
                    continue
                k, v = line.split(":", maxsplit=1)
                v = "# " + v.strip()
                v, c = gen.pandoc(cache_key + f"_header_{k}", mtime, v)
                cached &= c
                headers[k.lower()] = v
            assert "title" in headers, f"could not find 'title' for {filepath}"

            preview = ""
            while (line := f.readline()) and line.strip() != SEPERATOR:
                preview += line
            preview = preview.strip()
            preview, c = gen.pandoc(cache_key + "_preview", mtime, preview)
            cached &= c

            body, c = gen.pandoc(cache_key + "_body", mtime, f.read().strip())
            cached &= c
        return Post(
            mtime=mtime,
            headers=headers,
            preview=preview,
            body=body,
            year=year,
            month=month,
            day=day,
            name=name,
            is_draft=is_draft,
            cached=cached,
        )

    def title(self):
        return self.headers["title"]

    def uri(self):
        root = "/posts"
        if self.is_draft:
            root = "/drafts/posts"
        return f"{root}/{self.year}/{self.month}/{self.day}/{self.name}.html"

    def footer(self):
        pass


class Generator:
    BUILD_DIR = Path("build/")
    CACHE_DIR = Path("build/.cache")
    TEMPLATE_DIR = Path("templates/")

    # TODO - introduce a per-thread CacheManager object and parallelize builds
    accessed_cache_keys: set[str]

    post_header: str
    post_footer: str

    env: Environment

    def __init__(self):
        os.makedirs(Generator.CACHE_DIR, exist_ok=True)
        self.accessed_cache_keys = set()
        self.env = Environment(loader=FileSystemLoader(Generator.TEMPLATE_DIR))

    def pandoc(self, cache_key: str, mtime: float, input_: str) -> tuple[str, bool]:
        self.accessed_cache_keys.add(cache_key)

        cachepath = Generator.CACHE_DIR / cache_key
        if cachepath.exists() and mtime < cachepath.lstat().st_mtime:
            return cachepath.open().read(), True

        p = subprocess.Popen(
            ["pandoc", "-f", "markdown-smart", "-t", "html"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        output, _ = p.communicate(input_.encode())
        with cachepath.open("wb") as f:
            f.write(output)

        return output.decode(), False

    def cleanup_cache(self):
        for f in Generator.CACHE_DIR.iterdir():
            if f.name not in self.accessed_cache_keys:
                f.unlink()

    def build_index(self, posts: list[Post]):
        # This is never built from cache, it should be fast to build anyway
        rendered = self.env.get_template("index.html").render(
            posts=[p for p in posts if not p.is_draft]
        )
        index_file = Generator.BUILD_DIR / "index.html"
        with index_file.open("w") as f:
            f.write(rendered)

    def build_post(self, post: Post):
        post_file = Generator.BUILD_DIR / post.uri()[1:]
        os.makedirs(post_file.parent, exist_ok=True)
        if post_file.exists() and post_file.lstat().st_mtime > post.mtime:
            print("CACHED", post.name)
            return
        print("BUILT", post.name)

        rendered = self.env.get_template("post.html").render(post=post)
        with post_file.open("w") as f:
            f.write(rendered)

    def generate(self):
        # TODO - if any templates were modified, remove all uncached assets
        static_dir = Path("static").absolute()
        # Synchronize static/ with build/static/
        p = subprocess.Popen(
            "rsync --archive --delete --verbose".split()
            + [static_dir, Generator.BUILD_DIR],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        post_dir = Path("posts")
        posts = []
        for year_dir in post_dir.iterdir():
            for month_dir in year_dir.iterdir():
                for post in month_dir.glob("*.md"):
                    posts.append(Post.from_file(self, post))
        posts.sort(key=lambda x: (x.year, x.month, x.day), reverse=True)

        for post in posts:
            self.build_post(post)
        self.build_index(posts)
        self.cleanup_cache()

        p.wait()
        assert p.returncode == 0
        print("static/ copied successfully")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--watch", action="store_true")
    args = parser.parse_args()

    gen = Generator()
    gen.generate()
    if args.watch:
        p = subprocess.Popen(
            ["inotifywait", "-e", "modify", "-r", "-m", "posts"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        assert p.stdout
        os.set_blocking(p.stdout.fileno(), False)
        fds = [p.stdout]
        while True:
            r, _, e = select.select(fds, [], fds)
            if e:
                break
            while line := p.stdout.readline():
                continue
            gen = Generator()
            gen.generate()
            if p.returncode is not None:
                break
