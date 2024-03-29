quicksearch: a minimalistic webservice providing search abbreviations straight from any browser's address bar
=============================================================================================================

You've configured your browser to have search abbreviations for all your
most-used search engines and other useful sites.  
`woa velocity of unladen swallow` and there you are at [Wolfram
Alpha](https://www.wolframalpha.com/input/?i=velocity+of+unladen+swallow).

But what if you're using a friend's/colleague's browser without all that
convenience?  
`quicksearch` to the rescue: a tiny Python script that is programmable in the
same way — except it runs as a webserver and is thus usable from any browser
anywhere. (If you've got a domain to run it on, that is.)

That query from above would become something like `jjj.re/woa/velocity of
unladen swallow`. Not quite as convenient as your in-browser keywords, but
certainly faster than typing `wolframalpha.com` and waiting for 3.4 MB of
website to load just so you can type in your query.

Want to check out my stock version?  
There is a publicly accessible instance at [jjj.re](http://jjj.re/).  
(The site intentionally does not perform a redirect to HTTPS to save roundtrips
and thus time.)

Setup
-----

1. Clone repo to `/opt`

       git clone --recursive https://github.com/n-st/quicksearch.git /opt/quicksearch

2. Install requirements

       pip3 install -U flask twisted
       # Optionally, for phone number analysis:
       pip3 install -U phonenumbers
       # Optionally, for MAC/OUI lookup:
       wget -O data/oui.txt http://standards-oui.ieee.org/oui.txt

       # On Debian, you can instead use the (slightly older) versions from the official package repository:
       apt install python3-flask python3-twisted python3-phonenumbers

3. Copy `quicksearch.service` to your systemd service directory

       cp /opt/quicksearch/quicksearch.service /etc/systemd/system

4. Check where `pip` installed `twistd3` on your system,
   adjust path in service file if necessary

       which twistd3
       vim /etc/systemd/system/quicksearch.service

5. Adapt path, port, and bindhost settings to your needs

       grep Environment= /etc/systemd/system/quicksearch.service
       vim /etc/systemd/system/quicksearch.service

6. Enabled and start service

       systemctl enable --now quicksearch.service

Non-redirect functionality
--------------------------

Over time, `quicksearch` evolved to also contain a few additional features
beyond mere search redirections:

- `/ip`  
  Print the IP address from which the user is connecting:

      203.0.113.89

  or

      2001:db8:78a3:9889:5bd1:b3e5:bb52:ed80

- `/mac/48-2C-6A-1E-59-3D` or `/oui/48-2C-6A-1E-59-3D`
  Look up which organization this OUI is registered to.  
  Also supports other formats, e.g. `48-2C-6A-1E-59-3D`, `48:2C:6A:1E:59:3D`,
  `482c6a`, etc.

- `/telnum/+442072343456` or `/telnum/442072343456`  
  Print information about the phone number's origin country, region, and type:

      +44 20 7234 3456
      London, United Kingdom - fixed-line

- `/ula`  
  Generate a Unique Local IPv6 Unicast Address (ULA) according to the algorithm
  in RFC 4193, section 3.2.2.  
  The output is the network address (all host bits set to zero) of the ULA /48:

      fd6c:e2c3:fb9c::

Todos / Possible improvements
-----------------------------

- [ ] Show the last-updated date of the OUI file (from file modification date)
- [ ] Support IABs in OUI lookup
- [ ] Use netaddr for MAC parsing and (fallback) OUI lookup
