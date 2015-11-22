# ======================================================================
# >> IMPORTS
# ======================================================================

from collections import defaultdict
from engines.precache import Model

class _models(dict):
	def __missing__(self, item):
		self[item] = Model(item)
		return self[item]
models = _models()