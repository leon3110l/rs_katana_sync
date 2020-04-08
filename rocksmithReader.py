from memoryReader import MemoryReader


class RocksmithReader():
    def __init__(self):
        self.reader = MemoryReader("Rocksmith2014.exe")

    def get_song_id(self):

        song = self.reader.read_string(self.reader.read_pointer(self.reader.get_base() + 0x00F5C494, [0xBC]))

        return song.lower().replace("play_", "").replace("_preview", "")