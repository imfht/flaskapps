class Error(Exception):

    """Base class for exceptions in this module."""
    pass


class BlueprintError(Error):

    def __init__(self):
        self.msg = "Cannot register Blueprints"

    def __str__(self):
        return repr(self.msg)


        
#Error for incase strings are not replaced in files
class ReplaceError(Error):

    def __init__(self, error_msg):
        self.msg = error_msg

    def __str__(self):
        return repr(self.msg)
