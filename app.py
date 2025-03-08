#!/usr/bin/env python3

from feedfinder2 import find_feeds
from flask import Flask
from flask import abort, redirect, url_for
from flask import render_template
from flask import request
from reader import make_reader

reader = make_reader("db.sqlite")

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
    return render_template('feeds.html', feeds=feeds)

@app.post("/feeds")
def add_feed():
    f = request.form['url']
    reader.add_feed(f, exist_ok=True)
    reader.update_feeds()
    return redirect(url_for("list_feeds"))

