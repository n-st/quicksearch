#!/usr/bin/env python3
# encoding: utf-8 (as per PEP 263)

from flask import Flask, Response, abort, redirect, request, send_file, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from urllib.parse import quote, quote_plus, unquote, unquote_plus
import os
import glob
import re
import ipaddress
try:
    import telnum
except:
    import sys
    sys.stderr.write('Could not import telnum module. Telnum functionality will be disabled.\n')
try:
    import ula
except:
    import sys
    sys.stderr.write('Could not import ula module. ULA functionality will be disabled.\n')

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route('/')
def root():
    searches = []
    redirects = []
    header = []
    s_header = []
    r_header = []

    header += ['QuickSearch']
    header += ['===========']
    s_header += ['']
    s_header += ['The following search providers are defined:']
    s_header += ['']
    r_header += ['']
    r_header += ['The following static redirections are defined:']
    r_header += ['']

    for rule in app.url_map.iter_rules():
        if rule.endpoint in ['static', 'root']:
            continue

        url = request.url_root.rstrip('/') + re.sub(r'<(.+:)?(.+)>', r'…', str(rule))
        url = url.rpartition('://')[2]
        line = unquote("* {:40s} {}".format(rule.endpoint, url))

        if '…' in url:
            searches.append(line)
        else:
            redirects.append(line)

    response_lines = header
    if searches:
        response_lines += s_header
        response_lines += sorted(searches)
    if redirects:
        response_lines += r_header
        response_lines += sorted(redirects)

    return Response(
            '\n'.join(response_lines)+'\n',
            mimetype='text/plain'
            )

def simple_query_handler(url, query):
    search_str = query
    if request.query_string:
        search_str += '?' + request.query_string.decode('utf-8')

    return redirect(url % quote_plus(search_str), code=303)

def static_redirect_handler(url):
    return redirect(url, code=303)

def print_client_ip_handler():
    addr = ipaddress.ip_address(request.remote_addr)

    if type(addr) == ipaddress.IPv6Address and addr.ipv4_mapped:
        addr = addr.ipv4_mapped

    return Response(
            str(addr) + '\n',
            mimetype='text/plain'
            )

try:
    import telnum

    def telnum_info_handler(num):
        return Response(
                telnum.number_to_text(num) + '\n',
                mimetype='text/plain'
                )

    @app.route('/telnum/<path:num>')
    def phone_number_info(num):
        return telnum_info_handler(num)

except:
    # Oh well.
    pass

try:
    import ula

    @app.route('/ula')
    def ipv6_unique_local_address():
        return Response(
                str(ula.generate_ula()) + '\n',
                mimetype='text/plain'
                )

except:
    # Oh well.
    pass

GITIGNORE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'github-gitignore')
OUI_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'oui.txt')

if os.path.isdir(GITIGNORE_PATH):
    @app.route('/gitignore/<string:query>')
    @app.route('/ignore/<string:query>')
    def gitignore_template(query):
        query_filename = '%s.gitignore' % query
        for filename in glob.glob(os.path.join(GITIGNORE_PATH, '*.gitignore')) + glob.glob(os.path.join(GITIGNORE_PATH, 'Global', '*.gitignore')):
            if filename.lower().endswith(query_filename.lower()):
                return send_file(filename, mimetype='text/plain')
        # If we get this far, nothing was found:
        return Response(
                '# No gitignore file found for "%s"\n' % query,
                mimetype='text/plain'
                ), 404

if os.path.isfile(OUI_PATH):
    @app.route('/mac/<string:query>')
    @app.route('/oui/<string:query>')
    def oui_lookup(query):
        if not os.path.isfile(OUI_PATH):
            return Response(
                    'Error\nOUI file missing\n',
                    mimetype='text/plain'
                    ), 500

        # transform OUI into format 3C-D9-2B
        match = re.match('^([0-9A-Fa-f]{2})[:-]?([0-9A-Fa-f]{2})[:-]?([0-9A-Fa-f]{2})', query)
        if not match:
            return Response(
                    'Error\nInvalid input (not an EUI)\n',
                    mimetype='text/plain'
                    ), 400

        oui = '%s-%s-%s' % match.groups()
        oui = oui.upper()

        octet1 = int(match.group(1), 16)
        if octet1 & (1<<1):
            return Response(
                    '%s\nlocally administered address\n' % (oui),
                    mimetype='text/plain'
                    ), 200

        with open(OUI_PATH, 'r') as f:
            for line in f:
                if line.startswith(oui):
                    parts = line.split(maxsplit=2)
                    if len(parts) != 3:
                        return Response(
                                'Error\nFormat error in OUI file\n',
                                mimetype='text/plain'
                                ), 500
                    organization = parts[-1]
                    return Response(
                            '%s\n%s\n' % (oui, organization),
                            mimetype='text/plain'
                            ), 200

        return Response(
                '%s\nNo organisation found\n' % oui,
                mimetype='text/plain'
                ), 404

else:
    @app.route('/mac/<path:query>')
    @app.route('/oui/<path:query>')
    def mac_address_vendor_lookup(query):
        return simple_query_handler('http://coffer.com/mac_find/?string=%s', query)


@app.route('/clean/<path:query>')
@app.route('/cleango/<path:query>')
@app.route('/go/<path:query>')
def url_clean(query):
    # re-add GET parameters to query URL that will be parsed
    if request.query_string:
        query += '?' + request.query_string.decode('utf-8')

    print(query)

    url = None

    # Google URL format:
    # https://www.google.com/url?sa=t&source=web&rct=j&url=https://www.example.com/page%3Fparam%3Dvalue&ved=2ahUKEwiY3OaWh-XpAhXytYsKHZSOBaAQwqsBMAF6BAgHEAg&usg=AOvVaw2r6f5XJRxROXt-aRr_r3lI
    match = re.match(r'^https?://www\.google\.com/url?.*url=([^&]+)', query)
    if match:
        url = unquote(match.group(1))

    # AMP URL format:
    # https://www.google.com/amp/s/www.theregister.co.uk/AMP/2015/09/15/still_200k_iot_heartbleed_vulns/
    # -> https://www.theregister.co.uk/2015/09/15/still_200k_iot_heartbleed_vulns/
    # https://www.google.com/amp/s/www.golem.de/news/fuzzing-wie-man-heartbleed-haette-finden-koennen-1504-113345.amp.html
    # -> https://www.golem.de/news/fuzzing-wie-man-heartbleed-haette-finden-koennen-1504-113345.html
    match = re.match(r'^(https?://)www\.google\.com/amp/s/(.+)', query)
    if match:
        url = match.group(1) + match.group(2)
        url = re.sub(r'([^a-zA-Z0-9])[Aa][Mm][Pp]\1', r'\1', url)

    # Amazon URL format:
    # https://www.amazon.de/DSLRKIT-Ethernet-Splitter-Development-Raspberry/dp/B074Y6M67F/ref=foo_bar_1234_0?_encoding=UTF8&etcpp
    match = re.match(r'^(https://)(www\.|smile\.)?amazon\.([a-z]{2,3})/.*dp/([A-Z0-9]{10}/)', query)
    if match:
        url = match.group(1) + 'www.amazon.' + match.group(3) + '/dp/' + match.group(4)

    if not url:
        return Response(
                'Error\nInvalid input (URL format not recognised)\n',
                mimetype='text/plain'
                ), 400

    if request.path.startswith('/cleango/') or request.path.startswith('/go/'):
        return static_redirect_handler(url)
    else:
        return Response(
                '%s\n' % (url),
                mimetype='text/plain'
                ), 200

@app.route('/urldecode/<path:query>')
@app.route('/ud/<path:query>')
def urldecode(query):
    return Response(
            '%s\n' % (unquote(query)),
            mimetype='text/plain'
            ), 200

@app.route('/urlencode/<path:query>')
@app.route('/ue/<path:query>')
def urlencode(query):
    if request.query_string:
        query += '?' + request.query_string.decode('utf-8')
    return Response(
            # Browser automatically quote some characters, so we need to
            # unquote them to get a uniform (completely unquoted) starting
            # point
            '%s\n' % (quote(unquote(query))),
            mimetype='text/plain'
            ), 200

@app.route('/ula.ext')
def ipv6_unique_local_address_external():
    return static_redirect_handler('http://simpledns.com/private-ipv6.aspx')

@app.route('/ip')
def whats_my_ip():
    return print_client_ip_handler()

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

@app.route('/inwx/<path:query>')
def domain_check_inwx(query):
    return simple_query_handler('https://www.inwx.de/de/domain/check#search=%s#region=DEFAULT#rc=rc1', query)

@app.route('/ovh/<path:query>')
def domain_check_ovh(query):
    return simple_query_handler('https://www.ovh.de/cgi-bin/newOrder/order.cgi?domain_domainChooser_domain=%s', query)

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

@app.route('/repo')
def packages_repology_stats():
    return static_redirect_handler('https://repology.org/repositories/statistics')

@app.route('/repo/<path:query>')
def packages_repology_search(query):
    return simple_query_handler('https://repology.org/projects/?search=%s', query)

@app.route('/fport/<path:query>')
@app.route('/fports/<path:query>')
@app.route('/freshports/<path:query>')
def packages_freebsd_freshports(query):
    return simple_query_handler('https://www.freshports.org/search.php?num=20&query=%s', query)

@app.route('/gpkg/<path:query>')
@app.route('/eix/<path:query>')
def packages_gentoo(query):
    return simple_query_handler('https://packages.gentoo.org/packages/search?q=%s', query)

@app.route('/mensa')
def mensa_uni_passau():
    return static_redirect_handler('http://www.stwno.de/infomax/daten-extern/html/speiseplaene.php?einrichtung=UNI-P')

@app.route('/strings.sh')
@app.route('/bash-strings')
def bash_string_manipulation():
    return static_redirect_handler('http://tldp.org/LDP/abs/html/string-manipulation.html')

@app.route('/denic/<path:query>')
def denic_web_whois(query):
    return simple_query_handler('https://www.denic.de/webwhois-web20/?domain=%s', query)

@app.route('/ssll/<path:query>')
def ssllabs(query):
    return simple_query_handler('https://www.ssllabs.com/ssltest/analyze.html?d=%s&hideResults=on&latest', query)

@app.route('/bgp/<path:query>')
def hurricane_electric_bgp(query):
    return simple_query_handler('http://bgp.he.net/search?commit=Search&search[search]=%s', query)

@app.route('/tld/<path:query>')
def tldlist_tld_info(query):
    return simple_query_handler('https://tld-list.com/tld/%s', query)

@app.route('/woa/<path:query>')
def wolfram_alpha(query):
    return simple_query_handler('https://www.wolframalpha.com/input/?i=%s', query)

@app.route('/dcc/<path:query>')
def dict_cc(query):
    return simple_query_handler('https://www.dict.cc/?s=%s', query)

@app.route('/gif/<path:query>')
def giphy(query):
    return simple_query_handler('http://giphy.com/search/%s', query)

@app.route('/fp')
def facepalm():
    return static_redirect_handler('http://i3.kym-cdn.com/photos/images/original/000/001/582/picard-facepalm.jpg')

@app.route('/randname')
def randname():
    return static_redirect_handler('http://www.behindthename.com/random/random.php?number=1&gender=u&surname=&nodiminutives=yes&all=yes')

@app.route('/hps/<string:query>')
def xmr_mining_calculator(query):
    return simple_query_handler('https://www.cryptocompare.com/mining/calculator/xmr?HashingPower=%s&HashingUnit=H%%2Fs&PowerConsumption=0', query)

@app.route('/ukcomp/<path:query>')
def uk_company_registrations(query):
    return simple_query_handler('https://beta.companieshouse.gov.uk/search?q=%s', query)

@app.route('/uci/<path:query>')
@app.route('/unicode/<path:query>')
def unicode_character_inspector(query):
    return simple_query_handler('https://apps.timwhitlock.info/unicode/inspect?s=%s', query)

@app.route('/ucs/<path:query>')
@app.route('/sunicode/<path:query>')
def unicode_character_search(query):
    return simple_query_handler('http://www.fileformat.info/info/unicode/char/search.htm?q=%s&preview=entity', query)

@app.route('/wiki/<path:query>')
@app.route('/enwiki/<path:query>')
def wikipedia_en(query):
    return simple_query_handler('https://en.wikipedia.org/w/index.php?search=%s', query)

@app.route('/dewiki/<path:query>')
def wikipedia_de(query):
    return simple_query_handler('https://de.wikipedia.org/w/index.php?search=%s', query)

@app.route('/rfc/<int:query>')
def rfc_by_number(query):
    return simple_query_handler('https://tools.ietf.org/html/rfc%s', str(query))

@app.route('/rfc/<path:query>')
def rfc_text_search(query):
    return simple_query_handler('https://tools.ietf.org/googleresults?q=%s', query)

@app.route('/ark/<path:query>')
def intel_ark(query):
    return simple_query_handler('https://ark.intel.com/content/www/us/en/ark/search.html?q=%s', query)

if __name__ == '__main__':
    app.run()
