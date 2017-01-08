class ParsingError(Exception):
    def __init__(self, error_msg):
        Exception.__init__(self)
        self.error_msg = error_msg

    def __str__(self):
        return repr(self.error_msg)
