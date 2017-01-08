try:
    from cStringIO import StringIO # Better option if available
except:
    from StringIO import StringIO
import string
from bencode import Bencode_Static
from errorhandler import ParsingError


class TorrentStr(object):
    # Core Class for stepping through Bencoded stream

    # Import Bencode Constants
    STR_LEN_VALUE_SEP = Bencode_Static.STR_LEN_VALUE_SEP
    INT_END = Bencode_Static.INT_END
    INT_START = Bencode_Static.INT_START

    def __init__(self, torr_str):
        self.torr_str = StringIO(torr_str)
        self.curr_char = None

    def next_char(self):
        self.curr_char = self.torr_str.read(1) #Grab a Character
        return self.curr_char # Return Character

    def step_back(self, position=-1, mode=1):
        #Step back, by N position relative to the current position.
        self.torr_str.seek(position, mode)

    def parse_str(self):
        #Parse and return a string from the torrent file content.
        '''
        Byte Strings:
        Byte strings are encoded as follows: <string length encoded in base ten ASCII>:<string data>
        Note that there is no constant beginning delimiter, and no ending delimiter.

        Example: 4: spam represents the string "spam"
        Example: 0: represents the empty string ""
        Format: <string length>:<string>
        d9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:home
        '''

        str_len = self.parse_number(delimiter=self.STR_LEN_VALUE_SEP)

        if not str_len:
            raise ParsingError('Empty string length found while parsing at position %d' % self.torr_str.pos)

        return self.torr_str.read(str_len)

    def parse_int(self):
        #Parse and return an integer from the torrent file content.
        '''
        Integers:
        Integers are encoded as follows: i<integer encoded in base ten ASCII>e
        The initial i and trailing e are beginning and ending delimiters.

        Example: i3e represents the integer "3"
        Example: i-3e represents the integer "-3"
        i-0e is invalid. All encodings with a leading zero, such as i03e, are invalid, other than i0e, which of course corresponds to the integer "0".

        NOTE: The maximum number of bit of this integer is unspecified, but to handle it as a signed 64bit integer is mandatory to handle "large files" aka .torrent for more that 4Gbyte.
        Format i[0-9]+e
        '''

        self.step_back() # just to make sure we are parsing the integer of correct format

        if self.next_char() != self.INT_START:
            raise ParsingError('Error while parsing for an integer. Found %s at position %d while %s is expected.' %
                               (self.curr_char, self.torr_str.pos, TorrentParser.INT_START))
        return self.parse_number(delimiter=self.INT_END)

    def parse_number(self, delimiter):
        ''' Parses a sequence of digits representing either an integer or string length and returns the number. '''
        parsed_int = ''
        while True:
            parsed_int_char = self.next_char()
            if parsed_int_char not in string.digits:
                if parsed_int_char != delimiter:
                    raise ParsingError('Invalid character %s found after parsing an integer (%s expected) at position %d.' %
                                       (parsed_int_char, delimiter, self.torr_str.pos))
                else:
                    break
            parsed_int += parsed_int_char
        return int(parsed_int)
