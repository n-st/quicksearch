#!/usr/bin/env python3

from flask import Flask, redirect, request
from urllib.parse import quote

app = Flask(__name__)

@app.route('/')
def root():
    return ''

def simple_query_handler(url, query):
    search_str = query
    if request.query_string:
        search_str += '?' + request.query_string.decode('utf-8')

    return redirect(url % quote(search_str), code=303)

@app.route('/google/<path:query>')
@app.route('/g/<path:query>')
def slash_google(query):
    return simple_query_handler('https://www.google.com/search?q=%s', query)

if __name__ == '__main__':
    app.run()
