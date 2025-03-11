#!/usr/bin/env python3

from feedfinder2 import find_feeds
from flask import Flask
from flask import redirect, url_for
from flask import render_template
from flask import request
from reader import make_reader
import feed_slugs
import random


reader = make_reader("db.sqlite", plugins=[feed_slugs.init_reader])

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/url")
def url():
    url = request.args.get('url', '')
    feeds = find_feeds(url)
    return render_template('url.html', url=url, feeds=feeds)


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
