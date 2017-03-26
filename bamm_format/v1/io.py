from abc import ABCMeta, abstractmethod


class BaMMModel(metaclass=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def get_version(self):
        pass

    @abstractmethod
    def get_metadata(self):
        pass

    @abstractmethod
    def set_metadata(self, key, value):
        pass

    @abstractmethod
    def del_metadata(self, key):
        pass

    @abstractmethod
    def __setitem__(self, tool_id, tool_data):
        pass

    @abstractmethod
    def __getitem__(self, tool_id):
        pass

    @abstractmethod
    def __delitem__(self, tool_id):
        pass

    @abstractmethod
    def add_attachment(self, attach_id, data):
        pass

    @abstractmethod
    def delete_attachment(self, attach_id, data):
        pass

    @abstractmethod
    def __iter__(self):
        return self


class BaMMModelFolder(BaMMModel):
    pass


class BaMMModelZip(BaMMModel):
    pass
