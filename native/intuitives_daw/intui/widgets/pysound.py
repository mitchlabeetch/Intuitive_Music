from intlib.lib import util
from intui.sgqt import *
import os


PYSOUND_FOLDER = os.path.join(util.HOME, "presets")

class pysound_file:
    """
    PURPOSE: A metadata-rich serialization format for plugin states and tags.
    ACTION: Parses and generates pipe-delimited preset files (.pysound) containing control values, versioning, and searchable tags.
    MECHANISM: 
        1. Encapsulates a control_dict mapping port IDs to integer values.
        2. string_to_data(): Iterates through newline-separated rows, splitting by the '|' delimiter to extract 'name', 'tag', 'hash', and port data.
        3. Supports 'version' tracking to ensure compatibility across different plugin iterations.
        4. Designed to be indexed by pysound_index for high-performance tag searches.
    """
    def __init__(self, **kwargs):
        self.name = None
        self.hash = None
        self.tags = []
        self.plugin = None
        self.version = []
        self.control_dict = {}
        assert(len(kwargs) == 1)
        if "a_path" in kwargs:
            self.string = util.read_file_text(kwargs["a_path"])
            self.string_to_data()
        elif "a_string" in kwargs:
            self.string = kwargs["a_string"]
            self.string_to_data()

    def string_to_data(self):
        for f_line in self.string.split("\n"):
            if f_line == "\\":
                break
            k, v = f_line.split("|")
            if k == "name":
                self.name = v
            elif k == "tag":
                self.tags.append(v)
            elif k == "hash":
                self.hash = v
            elif k == "plugin":
                self.plugin = v
            elif k == "version":
                self.version.append(v)
            else:
                self.control_dict[int(k)] = int(v)

    def data_to_string(self):
        f_result = ""
        raise NotImplementedError()
        return f_result

    def save_to_file(self, a_path):
        pass

class pysound_index:
    def __init__(self, a_plugin):
        pass

class pysound_indices:
    def __init__(self):
        self.tag_dict = {}

