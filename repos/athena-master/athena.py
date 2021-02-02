import sys
from urllib.parse import urljoin
from datetime import date, datetime
from flask import Flask, render_template, request
from flask_flatpages import FlatPages
from flask_frozen import Freezer
from flask_static_compress import FlaskStaticCompress
from werkzeug.contrib.atom import AtomFeed
from flatpandoc import FlatPagesPandoc
import subprocess as proc
import operator
import fileinput
import glob
import os
try:
  import config
except ImportError as e:
  print("Please run install.py first.")
  raise e

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FREEZER_REMOVE_EXTRA_FILES = False
FREEZER_BASE_URL = 'http://localhost/'

athena = Flask(__name__)
athena.config.from_object(__name__)
pages = FlatPages(athena)
freezer = Freezer(athena)
athena.jinja_env.comment_start_string = "{##}"
FlatPagesPandoc("markdown+raw_tex+yaml_metadata_block",
  athena, pre_render=True)
compress = FlaskStaticCompress(athena)

def make_external(url):
  return urljoin(request.url_root, url)

@athena.route("/feed.atom")
def recent_feed():
  feed = AtomFeed(config.config["title"],
      feed_url = request.url_root,
      url = request.url_root,
      subtitle = config.config["title"] + " Atom Feed"
    )

  for page in pages:
    if not page.meta.get("ispage"):
      feed.add(page["title"],
        str(page.__html__()),
          content_type = 'html',
          url = make_external("/posts/"+page.path),
          author = config.config["author"],
          updated = datetime.combine(page["date"], datetime.min.time()),
          published = datetime.combine(page["date"], datetime.min.time())
        )

  return feed.get_response()

@athena.route("/")
def index():
  posts = [page for page in pages if "ispage" not in page.meta]
  hpages = [page for page in pages if "ispage" in page.meta]
  return render_template("index.html", pages=posts,
                          hpages=hpages, config=config.config)

@athena.route("/<path:path>/")
def hardpagelink(path):
    hpage = ""
    for page in pages:
        if page.path == path:
            if page.meta["ispage"]:
                hpage = page
    hpages = [page for page in pages if "ispage" in page.meta]
    return render_template("hard.html", page=hpage,
                            hpages=hpages, config=config.config)

@athena.route("/posts/<path:path>/")
def page(path):
  page = pages.get_or_404(path)
  hpages = [page for page in pages if "ispage" in page.meta]
  return render_template("page.html", page=page,
                          hpages=hpages, config=config.config)

def cat():
  allp = os.path.join(os.getcwd(), "pages", "all.bib")
  bibs = os.path.join(os.getcwd(), "pages", "*.bib")
  with open(allp, "w") as f:
    for line in fileinput.input(glob.glob(bibs)):
      f.write(line)
    fileinput.close()

if __name__ == "__main__":
  cat()
  if len(sys.argv) > 1 and sys.argv[1] == "build":
    freezer.freeze()
  else:
    athena.run(port=5000)
