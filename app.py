#!/usr/bin/env python3

from auth import auth, login_required
from db import init_app
from feedfinder2 import find_feeds
from flask import flash
from flask import Flask
from flask import g
from flask import redirect, url_for
from flask import render_template
from flask import request
from nh3 import clean
from reader import make_reader, FeedExistsError
from urllib.parse import urlparse
import feed_slugs
import os
import random

app = Flask(__name__, static_url_path='')

reader = make_reader('db.sqlite', plugins=[feed_slugs.init_reader])
reader.enable_search()
reader.update_search()

app.config.from_mapping(SECRET_KEY='dev',DATABASE='db.sqlite')


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
    return render_template('home.html')


@app.get("/url")
def url():
    url = request.args.get('url', '')
    text = request.args.get('text', '')
    title = request.args.get('title', '')
    if url:
        feeds = find_feeds(url)
    else:
        feeds = find_feeds(text)
    return render_template('url.html', url=url, text=text, title=title,
                           feeds=feeds, get_feed=reader.get_feed)

@app.post("/url")
def add_url():
    f = request.form['url']
    return render_template("url.html", url=url)

@app.post("/entries")
def add_entry():
    link = request.form['link']

    o = urlparse(link)
    feed = o.scheme + "://" + o.netloc

    try:
        reader.add_feed(feed)
        reader.set_feed_slug(feed, generate_id())
        reader.disable_feed_updates(feed)
    except FeedExistsError:
        pass

    reader.add_entry({'feed_url': feed,'id': link}, overwrite=True)
    return redirect(url_for('show_feed',
                            slug=reader.get_feed_slug(feed)))

@app.get("/feeds")
def list_feeds():
    feeds = reader.get_feeds()
    return render_template('feeds.html', feeds=feeds, reader=reader)


@app.post("/feeds")
@login_required
def add_feed():
    f = request.form['url']
    reader.add_feed(f, exist_ok=True)
    reader.set_feed_slug(f, generate_id())
    reader.update_feeds()
    return redirect(url_for("list_feeds"))


@app.get("/feeds/<slug>")
def show_feed(slug):
    feed = reader.get_feed_by_slug(slug.lower())
    entries = reader.get_entries(feed=feed)
    return render_template('feed.html', feed=feed, entries=entries)

@app.post("/feeds/<slug>/delete")
@login_required
def delete_feed(slug):
    flash("i deleted " + slug + "...")
    feed = reader.get_feed_by_slug(slug.lower())
    reader.delete_feed(feed)
    return redirect(url_for("list_feeds"))

@app.route("/search", methods=['GET','POST'])
def search_entries():
    if request.method == 'POST':
        query = request.form['query']
        results = reader.search_entries(query)
        return render_template("search.html", query=query,
                               results=results, get_entry=reader.get_entry)
    return render_template("search.html")

def generate_id():
    chars = '0123456789abcdefghjkmnpqrstvwxyz'
    return ''.join(random.choice(chars) for _ in range(6))
