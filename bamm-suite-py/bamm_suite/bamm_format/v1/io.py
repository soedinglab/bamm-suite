from abc import ABCMeta, abstractmethod
from os.path import join, exists, isdir, isfile
import os
import json
# import ruamel.std.zipfile as zf
from bamm_format.utils import compute_checksum
from bamm_format.exceptions import *


class BaMMModel(metaclass=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def get_version(self):
        pass

    @abstractmethod
    def get_metadata(self, key):
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
    def __contains__(self, tool_id):
        pass

    @abstractmethod
    def add_attachment(self, attach_id, data):
        pass

    # NOTE: Since we delete the whole attach_id entry do we really need data?
    @abstractmethod
    def delete_attachment(self, attach_id):
        pass

    @abstractmethod
    def open_attachment(self, attach_id):
        pass

    @abstractmethod
    def __iter__(self):
        return self

    @abstractmethod
    def close(self):
        pass


class BaMMModelFolder(BaMMModel):

    def __init__(self, path):
        self._path = path
        self._general = {}
        self._general_changed = False
        self._metadata = {}
        self._metadata_changed = False
        self._path_attachments = join(self._path, "attachments")
        self._path_data = join(self._path, "data")
        self._path_general = join(self._path, "general.json")
        self._path_metadata = join(self._path, "metadata.json")
        self._attachments = set()
        self._open_attachments = set()  # NOTE: I think its better here to use a list instead of a set.
        self._deleted_files_data = set()
        self._data = {}
        self._modified_data = set()
        if not exists(self._path):
            self.create_model()
        elif isfile(self._path):
            raise BaMMModelInvalidError("Path %s is not a real BaMMModelFolder" % self._path)
        elif not self.is_valid_model():
            raise BaMMModelInvalidError("Path %s is not a real BaMMModelFolder" % self._path)
        self.load_data()

    def load_data(self):
        self._general = BaMMModelFolder.readjsonfile(self._path_general)
        self._metadata = BaMMModelFolder.readjsonfile(self._path_metadata)
        for _, _, files in os.walk(self._path_data):
            for f in files:
                # TODO: Make sure that a missing suffix, e.g. ".json" is not a problem here. For now files are saved without suffix.
                self._data[f] = BaMMModelFolder.readjsonfile(join(self._path_data, f))
        # Load attachments
        for _, _, files in os.walk(self._path_attachments):
            self._attachments = set(files)

    def create_model(self):
        os.makedirs(self._path)
        os.makedirs(self._path_data)
        os.makedirs(self._path_attachments)
        with open(self._path_general, "w") as f:
            json.dump(json.dumps({}), f)
        with open(self._path_metadata, "w") as f:
            json.dump(json.dumps({}), f)

    def get_version(self):
        return self._general["version"]

    @property
    def general(self):
        return None

    def get_general_key(self, key):
        if key in self._general:
            return self._general[key]
        return None

    @property
    def metada(self):
        """
        Metadata should only be read and changed via the get_metadata and set_metadata methods.
        :return: 
        """
        return None

    def get_metadata(self, key):
        if key in self._metadata:
            return self._metadata[key]
        return None

    def set_metadata(self, key, value):
        self._metadata[key] = value
        self._metadata_changed = True

    def del_metadata(self, key):
        del self._metadata[key]
        self._metadata_changed = True

    def __setitem__(self, tool_id, tool_data):
        self._data[tool_id] = tool_data
        if tool_id not in self._modified_data:
            self._modified_data.add(tool_id)
        if tool_id in self._deleted_files_data:
            self._deleted_files_data.remove(tool_id)

    def __getitem__(self, tool_id):
        if tool_id not in self._data:
            raise ToolMissingError("Tool %s not in BaMMModel" % tool_id)
        return self._data[tool_id]

    def __delitem__(self, tool_id):
        if tool_id not in self._data:
            raise ToolMissingError("Tool %s not in BaMMModel" % tool_id)
        del self._data[tool_id]
        if exists(join(self._path_data, tool_id)):
            self._deleted_files_data.add(tool_id)
        if tool_id in self._modified_data:
            self._modified_data.remove(tool_id)

    def __contains__(self, tool_id):
        return tool_id in self._data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()

    # NOTE: Not needed for now, since no handle is open after commit(). Keep for future.
    def close(self):
        pass

    def is_valid_model(self):
        return all([isdir(self._path), isdir(self._path_attachments), isdir(self._path_data),
                    isfile(self._path_general), isfile(self._path_metadata)])

    def add_attachment(self, attach_id, data, mode="wb", overwrite=True):
        """
        Add new attachment to the attachment folder. NOTE: For now only add new files and not new directories.
        NOTE: You can only add a new attachment, if you delete the old one first.
        TODO: Change to just overwrite.
        :param attach_id: 
        :param data: 
        :param mode:
        :param overwrite:
        :return: 
        """
        a_path = join(self._path_attachments, attach_id)
        if not overwrite and isfile(a_path):
            raise AttachmentAlreadyExistsError("Attachment %s already exists." % attach_id)
        with open(a_path, mode) as f:
            f.write(data)
        self._attachments.add(attach_id)

    def delete_attachment(self, attach_id):
        """
        Delete attachment.
        :param attach_id: 
        :return: 
        """
        if attach_id not in self._attachments:
            raise AttachmentMissingError("Attachment %s does not exists." % attach_id)
        a_path = join(self._path_attachments, attach_id)
        self._attachments.remove(attach_id)
        os.remove(a_path)

    def open_attachment(self, attach_id, mode="rw"):
        """
        Returns file handle to attachment. Connection should be closed by the caller.
        However to be sure, the commit method closes all handles to attachments.
        :param attach_id: 
        :param mode:
        :return: 
        """
        a_path = join(self._path_attachments, attach_id)
        if os.path.isdir(a_path):
            raise AttachmentInvalidError("Attachment %s is not a valid file name." % attach_id)
        a_handle = open(a_path, mode)
        self._open_attachments.add(a_handle)
        # NOTE: Afaik only "a" and "w" create new files. The rest should already be in the attachments set.
        if "a" in mode or "w" in mode:
            self._attachments.add(attach_id)
        return a_handle

    # Should this iterate over values or over keys?
    def __iter__(self):
        """
        Iterates over values in data.
        :return: 
        """
        for model in self._data:
            yield self._data[model]

    def commit(self):
        """
        commit applies all changes that have been made to the BaMMModel.
        Since a lot of attributes have to be reset, the method calls __init__() after the changes are made, 
        effectively reseting itself to the point of initialization, however with the changes made.
        commit() works in the following order:
        1. Write changes to existing elements and write new elements to data/ and attachments/. After each file is
        written, compute and save the according checksum.
        2. Write general.json and metadata.json
        3. Execute file deletions.
        NOTE: The way the class is implemented the order of executing shoud not matter (except for the checksums,
        which should be computed after a file is written.) However I specify the order here in case I made a mistake. 
        :return: 
        """
        if len(self._modified_data) > 0 or len(self._deleted_files_data) > 0 or self._metadata_changed:
            self._general_changed = True
        for handle in self._open_attachments:
            handle.close()
        for data_id in self._modified_data:
            d_path = join(self._path_data, data_id)
            with open(d_path, "w") as f:
                json.dump(json.dumps(self._data[data_id]), f)
                self._general["cksum_" + data_id] = compute_checksum(self._data[data_id])
        if self._metadata_changed:
            with open(join(self._path_metadata), "w") as f:
                json.dump(json.dumps(self._metadata), f)
        with open(join(self._path, "general.json"), "w") as f:
            json.dump(json.dumps(self._general), f)
        for rm_file in self._deleted_files_data:
            d_path = join(self._path_data, rm_file)
            os.remove(d_path)
        self.__init__(self._path)

    @staticmethod
    def readjsonfile(fpath):
        with open(fpath, "rb") as f:
            return json.loads(json.load(f))

    @staticmethod
    def writejsonfile(data, fpath):
        with open(fpath, "wb") as f:
            json.dump(json.dumps(data), f)


class BaMMModelZip(BaMMModel):

    def __init__(self, zip_path, sub_path, permission="w"):
        self.zip_path = zip_path
        self.subpath = sub_path
        self.permission = permission
        # self.zf_handle = zf.ZipFile(self.zip_path, permission)
        # make sure that directory is marked with an ending "/". Won't work with zip else.
        if not self.subpath.endsWith("/"):
            self.subpath += "/"
        self.general = None
        self.metadata = {}
        self.path_attachments = join(self.subpath, "attachments/")
        self.path_data = join(self.subpath, "data/")
        self.attachments = {}
        self.modified_attachments = []
        self.deleted_files = []
        self.data = {}
        self.modified_data = []
        self.deleted_files_data = []
        self.deleted_files_attachments = []
        self.zf_filelist = [x.filename for x in self.zf_handle.infolist()]
        if self.subpath not in self.zf_filelist:
            self.create_model()
        elif join(self.subpath, "general.json") not in self.zf_filelist:
            raise Exception("Path %s is not a real BaMMModelZip" % self.subpath)
        else:
            self.general = self.readjsonfile(join(self.subpath, "general.json"))
        if not self.is_valid_model():
            raise Exception("%s not a real BaMMModel!" % self.subpath)
        # Load metadata and general
        self.metadata = self.readjsonfile(join(self.subpath, "metadata.json"))


    def create_model(self):
        self.zf_handle.writestr(self.subpath,"")
        self.zf_handle.writestr(self.path_data,"")
        self.zf_handle.writestr(self.path_attachments, "")
        self.zf_handle.writestr(join(self.subpath, "general.json"), "")
        self.zf_handle.writestr(join(self.subpath, "metadata.json"), "")

    def get_version(self):
        return self.general["version"]

    def set_general(self, general):
        self.general = general

    def get_metadata(self):
        return self.metadata

    def set_metadata(self, key, value):
        self.metadata[key] = value

    def del_metadata(self, key):
        del self.metadata[key]

    def __setitem__(self, tool_id, tool_data):
        self.data[tool_id] = tool_data
        if tool_id not in self.modified_data:
            self.modified_data.append(tool_id)
        if tool_id in self.deleted_files:
            self.deleted_files_data.remove(tool_id)

    def __getitem__(self, tool_id):
        tool_path = join(self.subpath, "data", tool_id)
        if tool_path not in self.zf_filelist:
            raise Exception("Tool %s not in BaMMModel" % tool_id)
        return self.readjsonfile(tool_path)

    def __delitem__(self, tool_id):
        d_path = join(self.path_data, tool_id)
        if d_path not in self.zf_filelist and tool_id not in self.data:
            raise Exception("Tool_id %s does not exist." % tool_id)
        if d_path in self.zf_filelist:
            self.deleted_files_data.append(tool_id)
        if tool_id in self.data:
            del self.data[tool_id]
            self.modified_data.remove(tool_id)

    def extract_data(self, tool_id, ex_path=""):
        d_path = join(self.path_data, tool_id)
        if d_path not in self.zf_filelist:
            raise Exception("Data %s not found" % tool_id)
        self.zf_handle.extract(d_path, ex_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.close_connection()

    def close_connection(self):
        self.zf_handle.close()

    def is_valid_model(self):
        return True

    def add_attachment(self, attach_id, data):
        """
        Add new attachment to the attachment folder. NOTE: For now only add new files and not new directories.
        NOTE: You can only add a new attachment, if you delete the old one first.
        TODO: Change to just overwrite.
        :param attach_id: 
        :param data: 
        :return: 
        """
        #TODO: Just overwrite attachments.
        if attach_id in self.zf_filelist and attach_id not in self.deleted_files_attachments:
            raise Exception("Attachment %s already in model." % attach_id)
        self.attachments[attach_id] = data
        if attach_id not in self.modified_attachments:
            self.modified_attachments.append(attach_id)

    def delete_attachment(self, attach_id, data):
        a_path = join(self.path_attachments, attach_id)
        if a_path not in self.zf_filelist and attach_id not in self.attachments:
            raise Exception("Attachment %s does not exists." % attach_id)
        if attach_id in self.attachments:
            del self.attachments[attach_id]
        if a_path not in self.deleted_files:
            self.deleted_files_attachments.append(attach_id)

    def get_attachment(self, attach_id):
        """
        Returns attachment in byte-String format.
        :param attach_id: 
        :return: 
        """
        a_path = join(self.path_attachments, attach_id)
        if (a_path not in self.zf_filelist and attach_id not in self.attachments) or attach_id in self.deleted_files_attachments:
            raise Exception("Attachment %s not found." % attach_id)
        if attach_id in self.attachments:
            return self.attachments[attach_id]
        if a_path in self.zf_filelist:
            return self.zf_handle.read(a_path)

    def extract_attachment(self, attach_id, ex_path=""):
        """
        Extract attach_id to the specified path.
        :param attach_id: 
        :param ex_path: 
        :return: 
        """
        # TODO: Enable functionatlity to write attachments that in memory only. For now only works on things in zipfile.
        a_path = join(self.path_attachments)
        if a_path not in self.zf_filelist or attach_id in self.deleted_files_attachments:
            raise Exception("Attachment %s not found" % attach_id)
        self.zf_handle.extract(a_path, ex_path)

    def __iter__(self):
        for model in self.get_current_data():
            if model not in self.deleted_files_data:
                yield self.__getitem__(model)
            else:
                continue

    def get_current_data(self):
        return [ x for x in self.zf_filelist if x.beginsWith(self.path_data) and x.split("/")[-1] not in
                 self.deleted_files_data]

    def commit(self):
        """
        commit applies all changes that have been made to the BaMMModel.
        Since a lot of attributes have to be reset, the method calls __init__() after the changes are made, 
        effectively reseting itself to the point of initialization, however with the changes made.
        commit() works in the following order:
        1. Write changes to existing elements and write new elements to data/ and attachments/. After each file is
        written, compute and save the according checksum.
        2. Write general.json and metadata.json
        3. Execute file deletions.
        NOTE: The way the class is implemented the order of executing shoud not matter (except for the checksums,
        which should be computed after a file is written.) However I specify the order here in case I made a mistake. 
        :return: 
        """
        for attach_id in self.modified_attachments:
            a_path = join(self.path_attachments,attach_id)
            self.zf_handle.writestr(a_path, self.attachments[attach_id])
            # now compute checksum while you are at it.
            self.general["cksum_"+attach_id] = self.compute_checksum(join(self.path_attachments, attach_id))
        self.modified_attachments = []
        for data_id in self.modified_data:
            d_path = join(self.path_data, data_id)
            self.zf_handle.writestr(d_path, json.dumps(self.data[data_id]))
            # And now the checksum
            self.general["cksum_"+ data_id] = self.compute_ckecksum(self.data[data_id])
        self.modified_data = []
        self.zf_handle.writestr(join(self.subpath, "metadata.json"), json.dumps(self.metadata))
        self.zf_handle.writestr(join(self.subpath, "general.json"), json.dumps(self.general))
        self.zf_handle.close()
        for rm_file in self.deleted_files_data:
            d_path = join(self.path_data, rm_file)
            # zf.delete_from_zip_file(self.zip_path, d_path)
        for rm_file in self.deleted_files_attachments:
            a_path = join(self.path_attachments, rm_file)
            # zf.delete_from_zip_file(self.zip_path, a_path)
        # Reopen connection
        self.__init__(self.zip_path, self.subpath, self.permission)

    def readjsonfile(self, fpath):
        json_byte_str = self.zf_handle.read(fpath)
        return json.loads(json_byte_str)

    def compute_checksum(self, data):
        return 0

    def loadsubdirlist(self):
        return [x.filename for x in  self.zf_handle.infolist() if x.filename.beginsWith(self.subpath)]

    def subdirlist(self, prefixpath=None):
        if not prefixpath:
            prefixpath = self.subpath
        return [x.filename for x in self.zf_handle.infolist() if x.filename.beginsWith(prefixpath)]

    #TODO: This function.
    def close(self):
        pass

if __name__ == "__main__":
    import shutil
    bmmp = "temp/d1"
    if exists(bmmp):
        if isdir(bmmp):
            shutil.rmtree(bmmp)
        else:
            os.remove(bmmp)
    if not exists("temp"):
        os.mkdir("temp")
    with open(bmmp, "w") as f:
        f.write("sdfsdfsdfsfs")
    try:
        bm = BaMMModelFolder("temp/db/m1")
    except BaMMModelInvalidError:
        print("BaMMModelFolder could not be initialized correctly.")
    os.remove(bmmp)
    bm = BaMMModelFolder("temp/db/m1")
    print("Model was created correctly.")
    if exists(bm._path_data) and isdir(bm._path_data):
        print("Data folder setup.")
    if exists(bm._path_attachments) and isdir(bm._path_attachments):
        print("Attachment folder setup.")
    if exists(bm._path_general) and isfile(bm._path_general) and exists(bm._path_metadata) and isfile(bm._path_metadata):
        print("Setup ok")
    # More tests were done in the code environment.
    # import code
    # code.interact(local=locals())

    print("BaMMModelFolder initialized correctly.")
    # Do testing here.
    # 1. Create an empty model. Then fill it with data. Get that data. The change the data and check if the changes worked. Then close BaMMModel and see if it is the same when its opened again.
    # Then do the same for testing.
