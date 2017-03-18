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

That query from above would become something like `qrs.ovh/woa/velocity of
unladen swallow`. Not quite as convenient as your in-browser keywords, but
certainly faster than typing `wolframalpha.com` and waiting for 3.4 MB of
website to load just so you can type in your query.

Want to check out my stock version?  
There are publicly accessible instances at [qrs.ovh](http://qrs.ovh/) and
[jjjkm.win](http://jjjkm.win/).

Setup
-----

1. Clone repo to `/opt`

      git clone https://github.com/n-st/quicksearch.git /opt/quicksearch

2. Install requirements

      pip3 install -U flask twisted

3. Copy `quicksearch.service` to your systemd service directory

      cp /opt/quicksearch/quicksearch.service /etc/systemd/system

4. Check where `pip` installed `twistd` on your system,
   adjust path in service file if necessary

      which twistd
      vim /etc/systemd/system/quicksearch.service

5. Adapt path, port, and bindhost settings to your needs

      grep Environment= /etc/systemd/system/quicksearch.service
      vim /etc/systemd/system/quicksearch.service

6. Enabled and start service

      systemctl enable --now quicksearch.service
