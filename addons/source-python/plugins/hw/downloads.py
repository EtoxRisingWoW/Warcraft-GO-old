##
## IMPORTS
##

from core import AutoUnload
from events.manager import event_manager
from stringtables import string_tables

##
## LISTS
##

class _SoundsList(list):
    def __init__(self):
        super(_SoundsList, self).__init__()
        self._refresh_table_instance()

    def _refresh_table_instance(self):
        self.sound_table = string_tables.soundprecache

    def _add_to_sound_table(self, item):
        if self.sound_table is None:
            return
        self.sound_table.add_string(item, item)

    def server_spawn(self, game_event):
        self._refresh_table_instance()
        for item in self:
            item._set_all_downloads()
_sounds_list = _SoundsList()

event_manager.register_for_event(
    'server_spawn', _sounds_list.server_spawn)

class _DownloadablesList(list):
    def __init__(self):
        super(_DownloadablesList, self).__init__()
        self._refresh_table_instance()

    def _refresh_table_instance(self):
        self.download_table = string_tables.downloadables

    def _add_to_download_table(self, item):
        if self.download_table is None:
            return
        self.download_table.add_string(item, item)

    def server_spawn(self, game_event):
        self._refresh_table_instance()
        for item in self:
            item._set_all_downloads()
_downloadables_list = _DownloadablesList()

event_manager.register_for_event(
    'server_spawn', _downloadables_list.server_spawn)

class Downloadables(AutoUnload, set):
    def __init__(self):
        super(Downloadables, self).__init__()
        _downloadables_list.append(self)

    def add(self, item):
        if item in self:
            return
        _downloadables_list._add_to_download_table(item)
        if item.startswith('sound'):
        	_sounds_list._add_to_sound_table(item.replace('sound', '*'))
        super(Downloadables, self).add(item)

    def _set_all_downloads(self):
        for item in self:
            _downloadables_list._add_to_download_table(item)

    def _unload_instance(self):
        _downloadables_list.remove(self)

downloadables = Downloadables()