#!/usr/bin/env python3

from flask import Flask, Response, redirect, request, url_for
from urllib.parse import quote, quote_plus, unquote, unquote_plus
import re

app = Flask(__name__)

@app.route('/')
def root():
    output = []

    header = []
    header += ['QuickSearch']
    header += ['===========']
    header += ['']
    header += ['The following search providers are defined:']
    header += ['']

    for rule in app.url_map.iter_rules():
        if rule.endpoint in ['static', 'root']:
            continue

        url = request.url_root.rstrip('/') + re.sub(r'<(.+:)?(.+)>', r'', str(rule))

        line = unquote("* {:40s} {}".format(rule.endpoint, url))
        output.append(line)

    return Response(
            '\n'.join(header + sorted(output)),
            mimetype='text/markdown'
            )

def simple_query_handler(url, query):
    search_str = query
    if request.query_string:
        search_str += '?' + request.query_string.decode('utf-8')

    return redirect(url % quote_plus(search_str), code=303)

@app.route('/google/<path:query>')
@app.route('/g/<path:query>')
def google(query):
    return simple_query_handler('https://www.google.com/search?q=%s', query)

@app.route('/i/<path:query>')
@app.route('/gi/<path:query>')
def google_image(query):
    return simple_query_handler('https://www.google.com/search?q=%s&tbm=isch', query)

@app.route('/v/<path:query>')
@app.route('/gv/<path:query>')
def google_video(query):
    return simple_query_handler('https://www.google.com/search?q=%s&tbm=vid', query)

@app.route('/tineye/<path:query>')
def tineye(query):
    return simple_query_handler('https://tineye.com/search?url=%s', query)

@app.route('/madison/<path:query>')
def madison(query):
    return simple_query_handler('https://qa.debian.org/madison.php?table=all&g=on&package=%s', query)

@app.route('/deb/<path:query>')
def madison_debian(query):
    return simple_query_handler('https://qa.debian.org/madison.php?table=debian&g=on&package=%s', query)

@app.route('/ubu/<path:query>')
def madison_ubuntu(query):
    return simple_query_handler('https://qa.debian.org/madison.php?table=ubuntu&g=on&package=%s', query)

@app.route('/dpkg/<path:query>')
def packages_debian(query):
    return simple_query_handler('https://packages.debian.org/search?keywords=%s', query)

@app.route('/upkg/<path:query>')
def packages_ubuntu(query):
    return simple_query_handler('http://packages.ubuntu.com/search?keywords=%s', query)

@app.route('/apkg/<path:query>')
def packages_archlinux(query):
    return simple_query_handler('https://www.archlinux.org/packages/?q=%s', query)

@app.route('/aur/<path:query>')
def packages_archuserrepo(query):
    return simple_query_handler('https://aur.archlinux.org/packages/?K=%s', query)

@app.route('/fport/<path:query>')
@app.route('/fports/<path:query>')
@app.route('/freshports/<path:query>')
def packages_freebsd_freshports(query):
    return simple_query_handler('https://www.freshports.org/search.php?num=20&query=%s', query)

if __name__ == '__main__':
    app.run()
