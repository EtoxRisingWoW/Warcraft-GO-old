﻿# ======================================================================
# >> IMPORTS
# ======================================================================


# Source.Python
from engines.sound import Sound

# Warcraft: GO
from wcgo.downloads import downloadables


# ======================================================================
# >> CLASSES
# ======================================================================

class _Sounds(dict):
	def __missing__(self, item):
		self[item] = Sound(None, 0, item.replace('sound', '*'))
		downloadables.add(item)
		return self[item]


# ======================================================================
# >> GLOBALS
# ======================================================================

sound_list = ['sound/source-python/wcgo/levelup.mp3']
sounds = _Sounds()
for sound in sound_list:
	instance = sounds[sound]