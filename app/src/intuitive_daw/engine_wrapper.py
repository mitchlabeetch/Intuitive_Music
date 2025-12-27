import ctypes
import os
import sys

# Path to the compiled shared library
# Assuming the user compiles it to app/native/engine/build/libintuitives_engine.so
# In a real scenario, this path resolution would be more robust.
LIB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../native/engine/build/libintuitives_engine.so"
)

class IntuitivesEngine:
    def __init__(self):
        self.lib = None
        try:
            self.lib = ctypes.CDLL(LIB_PATH)
            self.setup_signatures()
        except OSError:
            print(f"Warning: Could not load audio engine library at {LIB_PATH}. Please compile the C++ engine.")

    def setup_signatures(self):
        if not self.lib: return

        # DAW_AddTrack(const char* filePath)
        self.lib.DAW_AddTrack.argtypes = [ctypes.c_char_p]
        self.lib.DAW_AddTrack.restype = None

        # DAW_RemoveTrack(int index)
        self.lib.DAW_RemoveTrack.argtypes = [ctypes.c_int]
        self.lib.DAW_RemoveTrack.restype = None

        # DAW_Play()
        self.lib.DAW_Play.argtypes = []
        self.lib.DAW_Play.restype = None

        # DAW_PlayAll()
        self.lib.DAW_PlayAll.argtypes = []
        self.lib.DAW_PlayAll.restype = None

        # DAW_Stop()
        self.lib.DAW_Stop.argtypes = []
        self.lib.DAW_Stop.restype = None

        # DAW_IsPlaying()
        self.lib.DAW_IsPlaying.argtypes = []
        self.lib.DAW_IsPlaying.restype = ctypes.c_bool

        # DAW_LoadPlugin(const char* type, const char* path)
        self.lib.DAW_LoadPlugin.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.DAW_LoadPlugin.restype = None

    def add_track(self, file_path):
        if self.lib:
            self.lib.DAW_AddTrack(file_path.encode('utf-8'))

    def remove_track(self, index):
        if self.lib:
            self.lib.DAW_RemoveTrack(index)

    def play(self):
        if self.lib:
            self.lib.DAW_Play()

    def play_all(self):
        if self.lib:
            self.lib.DAW_PlayAll()

    def stop(self):
        if self.lib:
            self.lib.DAW_Stop()

    def is_playing(self):
        if self.lib:
            return self.lib.DAW_IsPlaying()
        return False

    def load_plugin(self, plugin_type, path):
        if self.lib:
            self.lib.DAW_LoadPlugin(plugin_type.encode('utf-8'), path.encode('utf-8'))

# Singleton instance
engine = IntuitivesEngine()
