import os
import subprocess
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import IO

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
    cached: bool

    @classmethod
    def from_file(cls, gen: "Generator", filepath: Path):
        month_dir = filepath.parent
        month = int(month_dir.stem)
        year_dir = month_dir.parent
        year = int(year_dir.stem)
        day = int(filepath.name.split("-")[0])
        name = filepath.stem

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
        return Post(mtime, headers, preview, body, year, month, day, name, cached)

    def title(self):
        return self.headers["title"]

    def footer(self):
        pass


class Generator:
    BUILD_DIR = Path("build/")
    CACHE_DIR = Path("build/.cache")
    TEMPLATE_DIR = Path("templates/")

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

        pass

    def build_post(self, post: Post):
        post_dir = Generator.BUILD_DIR / str(post.year) / str(post.month)
        os.makedirs(post_dir, exist_ok=True)
        post_file = (post_dir / post.name).with_suffix(".html")
        if post_file.exists() and post_file.lstat().st_mtime > post.mtime:
            print("CACHED", post.name)
            return

        rendered = self.env.get_template("post.html").render(post=post)
        with post_file.open("w") as f:
            f.write(rendered)

    def generate(self):
        # Synchronize static/ with build/static/
        os.system("rsync --archive --delete --verbose static build/static")

        post_dir = Path("posts")
        posts = []
        for year_dir in post_dir.iterdir():
            for month_dir in year_dir.iterdir():
                for post in month_dir.glob("*.md"):
                    posts.append(Post.from_file(self, post))

        for post in posts:
            self.build_post(post)
        self.build_index(posts)
        self.cleanup_cache()


if __name__ == "__main__":
    gen = Generator()
    gen.generate()
