"""
BaMMDatabase module that handles communication with multiple that BaMMModels that are put together in a Database structure.
"""

from abc import ABCMeta, abstractmethod
from zipfile import ZipFile, is_zipfile
from os.path import join, exists
import os
import json
import shutil
from contextlib import AbstractContextManager
from bamm_format.v1.io import BaMMModelFolder, BaMMModelZip
from bamm_format.exceptions import *


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

    # @christian: Did you write that comment or me?
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
    def __contains__(self, model_id):
        pass

    @abstractmethod
    def close(self):
        pass

class BaMMDatabaseFolder(BaMMDatabase):
    """
    BaMMs database in folder format.
    """

    def __init__(self, path):
        self._path = path
        self._path_info = join(self._path, "info.json")
        self._models = {}
        self._deleted_models = set()
        if not os.path.exists(self._path):
            self.create_database()
        elif os.path.isfile(self._path):
            raise BaMMDatabaseInvalidError("Invalid database path: %s" % self._path)
        for model in os.listdir(self._path):
            if os.path.isdir(join(self._path, model)):
                self._models[model] = BaMMModelFolder(join(self._path,model))

    def create_database(self):
        os.makedirs(self._path)  # Look over that line again.
        with open(self._path_info, "w") as f:
            json.dump(json.dumps({}), f)

    def __len__(self):
        return len(self._models)

    def create_model(self, model_id):
        if model_id in self._models:
            raise BaMMModelAlreadyExistsError("model_id %s already in database." % model_id)
        mpath = join(self._path, model_id)
        self._models[model_id] = BaMMModelFolder(mpath)

    def __getitem__(self, model_id):
        if model_id not in self._models:
            raise BaMMModelMissingError("model_id %s not found in database." % model_id)
        return self._models[model_id]

    def __delitem__(self, model_id):
        if model_id not in self._models:
            raise BaMMModelMissingError("model_id %s not found in database." % model_id)
        self._deleted_models.add(model_id)

    def __iter__(self):
        for model in self._models:
            yield self._models[model]

    def __enter__(self):
        return self

    def __contains__(self, model_id):
        return model_id in self._models

    def commit(self):
        for model in self._deleted_models:
            shutil.rmtree(join(self._path, model))
            del self._models[model]
        for model in self._models.values():
            model.commit()

    def __exit__(self, extype, exvalue, traceback):
        self.commit()

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
        # TODO: Write an empty json...
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


if __name__ == "__main__":
    # TODO: Replace with unittests
    dbpath = "temp/db"
    # Test folder database
    # At first Trigger invalid error
    if exists(dbpath):
        if os.path.isfile(dbpath):
            os.remove(dbpath)
        else:
            shutil.rmtree(dbpath)
    with open(dbpath, "w") as f:
        f.write("nfzasmdj;klfnk;sdaj")
    try:
        bmf = BaMMDatabaseFolder(dbpath)
    except BaMMDatabaseInvalidError:
        print("Correct exception triggered!")
    if exists(dbpath):
        os.remove(dbpath)
    bmf = BaMMDatabaseFolder(dbpath)
    if exists(dbpath) and exists(join(dbpath, "info.json")):
        print("Database successfully created!")
    bmf.create_model("m1")
    bmf.create_model("m2")
    try:
        bmf.create_model("m1")
    except BaMMModelAlreadyExistsError:
        print("Multiple models caught.")
    if exists(join(dbpath, "m1")):
        print("Model m1 created.")
    if len(bmf) == 2:
        print("2 Models correctly found.")
    bmf["m1"].set_metadata("blub", "m1_metadata")
    bmf["m2"].set_metadata("blub", "m2_metadata")
    if bmf["m1"].get_metadata("blub") == "m1_metadata" and bmf["m2"].get_metadata("blub") == "m2_metadata":
        print("Metadata read successful.")
    # Now test with context
    print("Now context manager!")
    try:
        cpy = bmf["m3"]
    except BaMMModelMissingError:
        print("Model correctly not found.")
    try:
        del bmf["m3"]
    except BaMMModelMissingError:
        print("Model was correctly not deleted.")
    del bmf["m2"]
    if len(bmf) == 1:
        print("Model was deleted correctly.")
    bmf.commit()
    bmf.close()
    with BaMMDatabaseFolder(dbpath) as bmf:
        try:
            bmf["m1"].set_metadata("blub", "m1 changed in context")
        except BaMMModelMissingError:
            print(bmf._models)
        for model in bmf:
            if model.get_metadata("blub") == "m1 changed in context":
                print("Metadata changed successful.")


    # Now do tests for the zip archive.

