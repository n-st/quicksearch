#!/usr/bin/env python3

from flask import Flask, redirect, request
from urllib.parse import quote, quote_plus

app = Flask(__name__)

@app.route('/')
def root():
    return ''

def simple_query_handler(url, query):
    search_str = query
    if request.query_string:
        search_str += '?' + request.query_string.decode('utf-8')

    return redirect(url % quote_plus(search_str), code=303)

@app.route('/google/<path:query>')
@app.route('/g/<path:query>')
def slash_google(query):
    return simple_query_handler('https://www.google.com/search?q=%s', query)

@app.route('/i/<path:query>')
@app.route('/gi/<path:query>')
def slash_google_img(query):
    return simple_query_handler('https://www.google.com/search?q=%s&tbm=isch', query)

@app.route('/v/<path:query>')
@app.route('/gv/<path:query>')
def slash_google_video(query):
    return simple_query_handler('https://www.google.com/search?q=%s&tbm=vid', query)

@app.route('/tineye/<path:query>')
def slash_tineye(query):
    return simple_query_handler('https://tineye.com/search?url=%s', query)

@app.route('/madison/<path:query>')
def slash_madison(query):
    return simple_query_handler('https://qa.debian.org/madison.php?table=all&g=on&package=%s', query)

@app.route('/deb/<path:query>')
def slash_deb(query):
    return simple_query_handler('https://qa.debian.org/madison.php?table=debian&g=on&package=%s', query)

@app.route('/ubu/<path:query>')
def slash_ubu(query):
    return simple_query_handler('https://qa.debian.org/madison.php?table=ubuntu&g=on&package=%s', query)

@app.route('/dpkg/<path:query>')
def slash_dpkg(query):
    return simple_query_handler('https://packages.debian.org/search?keywords=%s', query)

@app.route('/upkg/<path:query>')
def slash_upkg(query):
    return simple_query_handler('http://packages.ubuntu.com/search?keywords=%s', query)

@app.route('/apkg/<path:query>')
def slash_apkg(query):
    return simple_query_handler('https://www.archlinux.org/packages/?q=%s', query)

@app.route('/aur/<path:query>')
def slash_aur(query):
    return simple_query_handler('https://aur.archlinux.org/packages/?K=%s', query)

@app.route('/fport/<path:query>')
@app.route('/fports/<path:query>')
@app.route('/freshports/<path:query>')
def slash_freshports(query):
    return simple_query_handler('https://www.freshports.org/search.php?num=20&query=%s', query)

if __name__ == '__main__':
    app.run()
