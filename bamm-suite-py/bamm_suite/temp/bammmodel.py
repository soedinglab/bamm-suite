"""
Tmp bammmodel implementation for testing.
"""



class BaMMModelFolder(object):

    def __init__(self, path):
        self.path = path
        self.value = "default_meta_data"

    def get_metadata(self):
        return self.value

    def add_metadata(self,value):
        print("Meta data in %s changed to %s" %(self.path, value))
        self.value = value


class BaMMModelZip(object):
    pass