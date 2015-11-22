##
## IMPORTS
##

from hw.downloads import downloadables

from engines.sound import Sound

sound_list = ()

class Sounds(dict):
	def __missing__(self, item):
		self[item] = Sound(None, 0, item.replace('sound', '*'))
		downloadables.add(item)
		return self[item]

sounds = Sounds()

for sound in sound_list:
	instance = sounds[sound]