from rsrtools.files.welder import Welder
from pathlib import Path
import json

from rocksmithReader import RocksmithReader


indexed_dlc = {}
def index_dlc(base_path: str):
    for path in Path(base_path).rglob("*p.psarc"):
        welder = Welder(path, 'r')
        # print(path.joinpath())
        for index in welder:
            file_name = welder.arc_name(index)
            if("manifest" in file_name and file_name.endswith(".json") and not file_name.endswith("vocals.json")):
                dlc = json.loads(welder.arc_data(index).decode())
                for key, song in dlc['Entries'].items():
                    indexed_dlc[song['Attributes']['PreviewBankPath'].lower().replace("song_", "").replace("_preview.bnk", "")] = str(path.joinpath())

    # print(json.dumps(indexed_dlc, indent=4))
    print(str(len(indexed_dlc.keys())) + " dlc found and indexed")

if __name__ == "__main__":

    rs_reader = RocksmithReader()

    index_dlc('D:/games/SteamLibrary/steamapps/common/Rocksmith2014/dlc/')
    song_id = rs_reader.get_song_id()
    print(indexed_dlc[song_id])
    while(True):
        pass