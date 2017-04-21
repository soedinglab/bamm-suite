from abc import ABCMeta, abstractmethod
from os.path import join, exists
import os
import json
import hashlib
import ruamel.std.zipfile as zf


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
    def get_attachment(self, attach_id):
        # TODO: return filehandle
        pass

    @abstractmethod
    def __iter__(self):
        return self

    @abstractmethod
    def close(self):
        pass



class BaMMModelFolder(BaMMModel):

    def __init__(self, path):
        # TODO: Copy functionality with regards to laziness from zip variant.
        self.path = path
        self.general = None
        # TODO Version read form init
        self.metadata = None
        self.path_attachments = join(self.path, "attachments")
        self.path_data = join(self.path, "data")
        self.attachments = {}
        self.modified_attachments = []
        self.data = {}
        self.modified_data = []
        if not exists(self.path):
            self.create_model()
        elif not exists(join(self.path, "general.json")):
            raise Exception("Path %s is not a real BaMMModelFolder" % self.path)
        else:
            with open(join(self.path, "general.json")) as f:
                self.general = json.loads(json.load(f))
        if not self.is_valid_model():
            raise Exception("%s not a real BaMMModel!" % self.path)
        with open(join(self.path, "metadata.json")) as f:
            self.metadata = json.loads(json.load(f))

    def get_version(self):
        # TODO: Where do we store version? Assume in general.
        return self.general["version"]

    def get_metadata(self):
        return self.metadata

    def set_metadata(self, key, value):
        self.metadata[key] = value

    def del_metadata(self, key):
        #Do I really need this exception???
        if key not in self.metadata:
            raise Exception("Metadata %s not found." % key)
        del self.metadata[key]

    def __getitem__(self, item):
        # Load
        if item not in os.listdir(self.path_data):
            raise Exception("Data element %s not in BaMMModel." % item)
        # If its there load and return it.
        return json.loads(json.load(join(self.path_data, item)))

    def __setitem__(self, key, value):
        self.data[key] = value
        if key not in self.modified_data:
            self.modified_data.append(key)

    def __delitem__(self, key):
        datalist = os.listdir(self.path_data)
        if key not in datalist and key not in self.data:
            raise Exception("Item %s not in BaMMModel.." % key)
        if key in datalist:
            os.remove(join(self.path_data, key))
        del self.data[key]

    def add_attachment(self, attach_id, data):
        if attach_id in self.attachments:  # If we do it lazily also check for files.
            raise Exception("Attachment %s already in model." % attach_id)
        self.attachments[attach_id] = data
        self.modified_attachments.append(attach_id)

    def delete_attachment(self, attach_id, data):
        os_attachments_list = os.listdir(self.path_attachments)
        # If we didn't write it, just delete it from dictionary
        if attach_id in self.modified_attachments:
            del self.attachments[attach_id]
            self.modified_attachments.remove(attach_id)
        elif attach_id in os_attachments_list:
            os.remove(join(self.path_attachments, attach_id))
        else:
            raise Exception("Attachment %s not in Model." % attach_id)

    def get_attachment(self, attach_id):
        # Ok, do we really work with attachments??
        pass

    def __iter__(self):
        for data_id in os.listdir(self.path_data):
            yield json.loads(json.load(join(self.path_data, data_id)))

    def create_model(self):
        """
        Create directories and files for BaMMModel.
        :return: 
        """
        # TODO: Is there any standard information that we want to include? E.g. version.
        os.mkdir(self.path)
        os.mkdir(join(self.path, "data"))
        os.mkdir(join(self.path, "attachments"))
        open("general.json", "w").close()
        open("metadata.json", "w").close()
        self.general = {}
        self.metadata = {}

    def is_valid_model(self):
        """
        Check if checksums etc. fit the data.
        For this: Load the data, then do str(data).encode("utf-8") get the sha256.
        :return: 
        """
        # TODO Maybe do it on bytestreams instead...
        for data_id in os.listdir(self.path_data):
            tmp = json.loads(json.load(join(self.path_data, data_id)))
            hs = hashlib.sha3_256(str(tmp).encode("utf-8"))
            if hs != self.general["cksum_"+data_id]:
                return False
        return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Write modified data and attachments to file, then update checksums and write metadata and general to file. 
        :param exc_type: 
        :param exc_val: 
        :param exc_tb: 
        :return: 
        """
        self.commit()

    def commit(self):
        """
        commit applies all changes that have been made to the BaMMModel.
        :return: 
        """
        for attach_id in self.modified_attachments:
            with open(join(self.path_attachments, attach_id), "wb") as f:
                # maybe open in bytemode if non human readable stuff comes.
                f.write(self.attachments[attach_id])
            # now compute checksum while you are at it.
            self.general["cksum_"+attach_id] = self.compute_checksum(join(self.path_attachments, attach_id))
        self.modified_attachments = []
        for data_id in self.modified_data:
            with open(join(self.path_data, data_id), "w") as f:
                json.dump(json.dumps(self.data[data_id]), f)
            # And now the checksum
            self.general["cksum_" + data_id] = self.compute_ckecksum(self.data[data_id])
        self.modified_data = []
        with open(join(self.path, "metadata.json"), "w") as f:
            json.dump(json.dumps(self.metadata), f)
        with open(join(self.path, "general.json"), "w") as f:
            json.dump(json.dumps(self.general), f)

    @staticmethod
    def compute_checksum(data):
        return hashlib.sha256(str(data).encode("utf-8")).digest()


class BaMMModelFolder2(BaMMModel):

    def __init__(self,path):
        self.path = path
        self.general = None
        self.metadata = {}
        self.path_attachments = join(self.path, "attachments/")
        self.path_data = join(self.path, "data/")
        self.attachments = {}
        self.modified_attachments = []
        self.deleted_files = []
        self.data = {}
        self.modified_data = []
        self.deleted_files_data = []
        self.deleted_files_attachments = []
        if not exists(self.path):
            self.create_model()
            for _, _, files in os.walk(self.path_data):
                self.filelist = list(files)
        elif not exists(join(self.path, "general.json")):
            raise Exception("Path %s is not a real BaMMModelFolder" % self.path)
        else:
            self.general = self.readjsonfile(join(self.path, "general.json"))
        if not self.is_valid_model():
            raise Exception("%s not a real BaMMModel!" % self.path)
        # Load metadata and general
        self.metadata = json.loads(join(self.path, "metadata.json"))

    def create_model(self):
        os.makedirs(self.path)
        os.makedirs(self.path_data)
        os.makedirs(self.path_attachments)
        open(join(self.path, "general.json"), "w").close()
        open(join(self.path, "metadata.json"),"w").close()

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
        tool_path = join(self.path, "data", tool_id)
        if tool_path not in self.filelist:
            raise Exception("Tool %s not in BaMMModel" % tool_id)
        return self.readjsonfile(tool_path)

    def __delitem__(self, tool_id):
        d_path = join(self.path_data, tool_id)
        if d_path not in self.filelist and tool_id not in self.data:
            raise Exception("Tool_id %s does not exist." % tool_id)
        if d_path in self.filelist:
            self.deleted_files_data.append(tool_id)
        if tool_id in self.data:
            del self.data[tool_id]
            self.modified_data.remove(tool_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()

    # TODO: This function.
    def close(self):
        pass

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
        # TODO: Just overwrite attachments.
        if attach_id in self.filelist and attach_id not in self.deleted_files_attachments:
            raise Exception("Attachment %s already in model." % attach_id)
        self.attachments[attach_id] = data
        if attach_id not in self.modified_attachments:
            self.modified_attachments.append(attach_id)

    def delete_attachment(self, attach_id, data):
        a_path = join(self.path_attachments, attach_id)
        if a_path not in self.filelist and attach_id not in self.attachments:
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
        if (
                a_path not in self.filelist and attach_id not in self.attachments) or attach_id in self.deleted_files_attachments:
            raise Exception("Attachment %s not found." % attach_id)
        if attach_id in self.attachments:
            return self.attachments[attach_id]
        if a_path in self.filelist:
            with open(a_path) as f:
                return f.read()

    def __iter__(self):
        for model in self.get_current_data():
            if model not in self.deleted_files_data:
                yield self.__getitem__(model)
            else:
                continue

    def get_current_data(self):
        return [x for x in self.filelist if x.split("/")[-1] not in self.deleted_files_data]

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
            a_path = join(self.path_attachments, attach_id)
            with open(a_path,"w") as f:
                f.write(self.attachments[attach_id])
                self.general["cksum_" + attach_id] = self.compute_checksum(join(self.path_attachments, attach_id))
        self.modified_attachments = []
        for data_id in self.modified_data:
            d_path = join(self.path_data, data_id)
            with open(d_path, "wb") as f:
                json.dump(json.dumps(self.data[data_id]), f)
                self.general["cksum_" + data_id] = self.compute_ckecksum(self.data[data_id])
        self.modified_data = []
        with open(join(self.path, "metadata.json"), "w") as f:
            json.dump(json.dumps(self.metadata), f)
        with open(join(self.path, "general.json"), "w") as f:
            json.dump(json.dumps(self.general), f)
        for rm_file in self.deleted_files_data:
            d_path = join(self.path_data, rm_file)
            os.remove(d_path)
        for rm_file in self.deleted_files_attachments:
            a_path = join(self.path_attachments, rm_file)
            os.remove(a_path)
        # Reopen connection
        self.__init__(self.path)

    def readjsonfile(self, fpath):
        return json.loads(json.load(fpath))

    def compute_checksum(self, data):
        return 0

class BaMMModelZip(BaMMModel):

    def __init__(self, zip_path, sub_path, permission="w"):
        self.zip_path = zip_path
        self.subpath = sub_path
        self.permission = permission
        self.zf_handle = zf.ZipFile(self.zip_path, permission)
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
            zf.delete_from_zip_file(self.zip_path, d_path)
        for rm_file in self.deleted_files_attachments:
            a_path = join(self.path_attachments, rm_file)
            zf.delete_from_zip_file(self.zip_path, a_path)
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
    pass
    # Do testing here.
    # 1. Create an empty model. Then fill it with data. Get that data. The change the data and check if the changes worked. Then close BaMMModel and see if it is the same when its opened again.
    # Then do the same for testing.
