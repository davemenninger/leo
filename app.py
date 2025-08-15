#!/usr/bin/env python3

from auth import auth
from db import init_app
from feedfinder2 import find_feeds
from flask import Flask
from flask import g
from flask import redirect, url_for
from flask import render_template
from flask import request
from nh3 import clean
from reader import make_reader
import feed_slugs
import os
import random

app = Flask(__name__, static_url_path='')

db_file = os.path.join(app.instance_path, 'db.sqlite')
reader = make_reader(db_file, plugins=[feed_slugs.init_reader])
app.config.from_mapping(SECRET_KEY='dev',DATABASE=db_file)


init_app(app)

app.register_blueprint(auth)

@app.template_filter('clean')
def inject_clean(html):
    s = ""
    try:
        s = clean(html)
    except TypeError as e:
        print(e)
        pass

    return s


@app.route("/")
def home():
    reader.update_feeds()
    return render_template('home.html')


@app.route("/url")
def url():
    url = request.args.get('url', '')
    text = request.args.get('text', '')
    title = request.args.get('title', '')
    if url:
        feeds = find_feeds(url)
    else:
        feeds = find_feeds(text)
    return render_template('url.html', url=url, text=text, title=title, feeds=feeds)


@app.get("/feeds")
def list_feeds():
    feeds = reader.get_feeds()
    return render_template('feeds.html', feeds=feeds, reader=reader)


@app.post("/feeds")
def add_feed():
    f = request.form['url']
    reader.add_feed(f, exist_ok=True)
    reader.set_feed_slug(f, generate_id())
    reader.update_feeds()
    return redirect(url_for("list_feeds"))


@app.route("/feeds/<slug>")
def show_feed(slug):
    feed = reader.get_feed_by_slug(slug.lower())
    entries = reader.get_entries(feed=feed)
    return render_template('feed.html', feed=feed, entries=entries)


def generate_id():
    chars = '0123456789abcdefghjkmnpqrstvwxyz'
    return ''.join(random.choice(chars) for _ in range(6))
