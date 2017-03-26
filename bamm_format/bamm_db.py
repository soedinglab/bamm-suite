from abc import ABCMeta, abstractmethod

"""
intended usage examples:

    with BaMMDatabaseFolder('/tmp/db/') as db:
        for model in db:
            print(model.get_metadata())

    with BaMMDatabaseZip('/tmp/db.zip') as db:
        db['foo_model'].add_metadata('author', 'Mr. Foo Bar')
        db['foo_model']['peng'] = {'version': '1.0.0', 'foo': 'bar'}
        for model in db:
            del model['bamm']
        print(len(db))
"""


class BaMMDatabase(metaclass=ABCMeta):

    def __init__(self, path):
        pass

    @abstractmethod
    def create_database(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def create_model(self, model_id):
        pass

    @abstractmethod
    def __getitem__(self, model_id):
        pass

    @abstractmethod
    def __delitem__(self, model_id):
        pass

    @abstractmethod
    def __iter__(self):
        return self


class BaMMDatabaseFolder(BaMMDatabase):
    pass


class BaMMDatabaseZip(BaMMDatabase):
    pass
