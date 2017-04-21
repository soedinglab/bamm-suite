"""
BaMMDatabase module that handles communication with multiple that BaMMModels that are put together in a Database structure.
"""

from abc import ABCMeta, abstractmethod
from zipfile import ZipFile, is_zipfile
from os.path import join, exists
import os
import json
from contextlib import AbstractContextManager
#from bamm_format.v1.io import BaMMModel
#from temp.bammmodel import BaMMModel
from bamm_format.v1.io import BaMMModelFolder, BaMMModelZip


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


class BaMMDatabase(AbstractContextManager, metaclass=ABCMeta):

    @abstractmethod
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

    # use this instead of create model
    #@abstractmethod
    #def __setitem__(self, key, value):
    #    pass

    @abstractmethod
    def __getitem__(self, model_id):
        pass

    @abstractmethod
    def __delitem__(self, model_id):
        pass

    @abstractmethod
    def __iter__(self):
        return self

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, extype, exvalue, traceback):
        pass

    @abstractmethod
    def close(self):
        pass

class BaMMDatabaseFolder(BaMMDatabase):
    """
    BaMMs database in folder format.
    """

    def __init__(self, path):
        self.path = path
        self.models = {}
        if not os.path.exists(self.path):
            self.create_database()
        elif os.path.isfile(self.path):
            raise Exception("File already exists for database %s." % self.path)
        for dir, subdir, _ in os.walk(self.path):
            for model in subdir:
                self.models[model] = BaMMModelFolder(join(dir, model))

    def create_database(self):
        os.makedirs(self.path)  # Look over that line again.
        # TODO init empty info.json

    def __len__(self):
        return len(self.models)

    def create_model(self, model_id):
        if model_id in self.models:
            raise Exception("Model %s already in database." % model_id)
        mpath = join(self.path, model_id)
        # TODO move makedir part in BaMMModel initialization
        os.mkdir(mpath)
        self.models[model_id] = BaMMModelFolder(mpath)

    def __getitem__(self, model_id):
        if model_id not in self.models:
            raise Exception("model_id %s not found in database." % model_id)
        #return BaMMModel(self.models[model_id])
        return self.models[model_id]

    def __delitem__(self, model_id):
        if model_id not in self.models:
            raise Exception("model_id %s not found in database." % model_id)
        os.removedirs(join(self.path, model_id))
        del self.models[model_id]


    def __iter__(self):
        for model in self.models:
            yield self.models[model]


    def __enter__(self):
        return self

    def __exit__(self, extype, exvalue, traceback):
        for model in self.models.values():
            model.commit_changes()

    def __setitem__(self, key, value):
        pass

    def close(self):
        pass


class BaMMDatabaseZip(BaMMDatabase):
    """
    Database for BaMM in zip format.
    """

    def __init__(self, path):
        self.path = path
        if not exists(self.path):
            self.create_database()
        elif not is_zipfile(self.path):
            raise Exception("Target is not a zip file.")
        self.zf = ZipFile(path, "w")
        archive_info = self.zf.infolist()
        self.models = {}
        for zfinfo in archive_info:
            # TODO Find something better for this dirty dirty hack.
            if zfinfo.is_dir() and zfinfo.filename.count("/") == 1:
                self.models[zfinfo.filename] = BaMMModelZip(self.path, zfinfo.filename)


    def create_database(self):
        """
        Create an empty database.
        WITH WHICH INFO IS INFO.JSON TO BE INITIALIZED??
        """
        with ZipFile(self.path, "w") as zf:
            zf.write("info.json", "")

    def __len__(self):
        return len(self.models)

    def create_model(self, model_id):
        """
        Init empty model. Initialise the following files:
        general.json, metadata.json, data folder,
        attachments folder
        WHAT TO DO WITH MODEL_ID???
        
        """
        # self.zf.write(join(str(model_id), "general.json"), "")
        # self.zf.write(join(str(model_id), "metadata.json"), "")
        # self.zf.write(join(str(model_id), "data//"), "")
        # self.zf.write(join(str(model_id), "attachments//"), "")
        if model_id in self.models:
            raise Exception("Model %s already in database." %model_id)
        self.models[model_id] = BaMMModelZip(model_id)

    def __getitem__(self, model_id):
        # TODO How do we do this? Try to load the database directly from the zip archive or extract and load from there?
        if model_id not in self.models:
            raise Exception("Model %s not in Database." %model_id)
        return self.models[model_id]

    def __delitem__(self, model_id):
        if model_id not in self.models:
            raise Exception("Model %s not in Database." %model_id)
        # Removing something from a zip file is not really supported yet. So for now just override directory with
        # an empty string. Look for something better. This might be something: ruamel.std.zipfile
        self.zf.writestr(join(model_id,"/"), "")

    def __iter__(self):
        for model in self.models:
            yield self.models[model]

    def __enter__(self):
        return self

    def __exit__(self, extype, exvalue, traceback):
        self.commit()
        self.zf.close()

    # TODO: This function!!!!!
    def commit(self):
        pass

    def __setitem__(self, key, value):
        pass

    """
    BaMM_database/
    >info.json (command line call, time/date of call)
    
    >Bamm1/
    
    >> general.json
    >> metadata.json
    
    >> data/
    >>> bg-model.json 
    >>> peng.json
    >>> fdr_analysis.json
    >>> model_visualization.json
    >>> ...
    
    >> attachments/
    >>> attachment1.file
    >>> attachment2.file
    >>> ...
    
    >Bamm2/
    >> general.json
    ...
    """

if __name__ == "__main__":
    dbpath = "temp/db"
    # Test folder database
    if exists(dbpath):
        os.removedirs(dbpath)
    bmf = BaMMDatabaseFolder(dbpath)
    if exists(dbpath):
        print("Database successfully created!")
    bmf.create_model("m1")
    if exists(join(dbpath, "m1")):
        print("Model m1 created.")
    bmf.create_model("m2")
    if exists(join(dbpath,"m2")):
        print("Model m2 created.")
    bmf["m1"].add_metadata("m1_metadata")
    bmf["m2"].add_metadata("m2_metadata")
    print(bmf["m1"].get_metadata())
    print(bmf["m2"].get_metadata())
    # Now test with context
    print("Now context manager!")
    with BaMMDatabaseFolder(dbpath) as bmf:
        bmf["m1"].add_metadata("m1 changed in context")
        for model in bmf:
            print(model.get_metadata())

    # Now do tests for the zip archive.

