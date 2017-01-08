import os
import sys
from torrentparse import TorrentParser

if len(sys.argv) > 1:
    torrent_files = sys.argv[1:]
    for torrent_file in torrent_files:
        if os.path.exists(torrent_file):
            print 'Parsing file {}'.format(torrent_file)
        else:
            sys.exit('Unable to find file {}'.format(torrent_file))

for torrent_file in torrent_files:
    tp = TorrentParser(torrent_file)
    print "Torrent File Name: %s" % torrent_file
    print "Track URL: %s" % tp.get_tracker_url()
    print "Tracker Creation Date: %s" % tp.get_creation_date()
    print "Tracker Client Name: %s" % tp.get_client_name()
    print "Tracker File Details: %s" % tp.get_files_details()
    print "===="
