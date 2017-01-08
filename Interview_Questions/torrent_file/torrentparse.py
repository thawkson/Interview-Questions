from datetime import datetime
from glob import glob
import re
import string
import os
import types

from torrentstring import TorrentStr
from bencode import Bencode_Static
from errorhandler import ParsingError

class TorrentParser(object):
    # Import Bencode Constants
    DICT_START = Bencode_Static.DICT_START
    LIST_START = Bencode_Static.LIST_START
    DICT_LIST_END = Bencode_Static.DICT_LIST_END
    INT_START = Bencode_Static.INT_START


    def __init__(self, torrent_file_path):
        #Read in Torrent File

        if not isinstance(torrent_file_path, types.StringType):
            raise ValueError('Path of the torrent file expected in string format.')

        if not os.path.exists(torrent_file_path):
            raise IOError("No file found at '%s'" % torrent_file_path)

        with open(torrent_file_path) as torr_file:
            torrent_content = torr_file.read()
            self.torrent_str = TorrentStr(torrent_content)

        self.match = match=re.compile("([idel])|(\d+):|(-?\d+)").match
        self.parsed_torrent_file = self.parse_torrent()

    def get_tracker_url(self):
        #Returns the tracker URL from the parsed torrent file.
        return self.parsed_torrent_file.get('announce')


    def get_creation_date(self):
        #return time stamp
        time_stamp = self.parsed_torrent_file.get('creation date')
        if time_stamp:
            return time_stamp


    def get_client_name(self):
        #Returns the name of the client that created the torrent if present, from the parsed torrent file.
        return self.parsed_torrent_file.get('created by')


    def get_files_details(self):
        #Get name, length and checksum for each file in the torrent.

        parsed_files_info = [] # Create empty list for parsed file details
        files_info = self.parsed_torrent_file.get('info') # Do we have an info section in the torrent
        if files_info:
            multiple_files_info = files_info.get('files')
            if multiple_files_info: # Does this torrent contain multiple files
                for file_info in multiple_files_info:
                    parsed_files_info.append((os.path.sep.join(file_info.get('path')), file_info.get('length'), ))
            else:
                parsed_files_info.append((files_info.get('name'), files_info.get('length'), ))

        return parsed_files_info


    def parse_torrent(self):
        #Grab the next character
        parsed_char = self.torrent_str.next_char()

        if not parsed_char: return # Nothing left to parse we're at the end

        # Start of character parsing logic
        if parsed_char == self.DICT_LIST_END: # Are we at the end of a dictionary
            return

        elif parsed_char == self.INT_START: # Are we at the beginning of an int
            return self.torrent_str.parse_int()

        elif parsed_char in string.digits: # string
            self.torrent_str.step_back()
            return self.torrent_str.parse_str()

        elif parsed_char == self.DICT_START: # Are we at the beginning of a dictionary
            parsed_dict = {}
            while True:
                dict_key = self.parse_torrent()
                if not dict_key:
                    break # End of dict
                dict_value = self.parse_torrent() # parse value
                parsed_dict.setdefault(dict_key, dict_value)
            return parsed_dict

        elif parsed_char == self.LIST_START: # Are we at the begininng of a List
            parsed_list=[]
            while True:
                list_item = self.parse_torrent()
                if not list_item:
                    break # End of list
                parsed_list.append(list_item)
            return parsed_list
