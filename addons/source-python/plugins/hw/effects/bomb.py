# ======================================================================
# >> IMPORTS
# ======================================================================

from hw.effects import models

from effects import temp_entities
from entities.entity import Entity
from events import Event
from filters.entities import EntityIter
from filters.recipients import RecipientFilter

global _smokestack
_smokestack = None

_tick_model = models['sprites/laser.vmt']
	
# ======================================================================
# >> EVENTS
# ======================================================================

@Event('bomb_planted')
def bomb_planted(event):
	for ent in EntityIter('planted_c4'):
		break
		
	entity = Entity.create('env_smokestack')
	entity.origin = ent.origin
	for output in ('basespread 8', 'spreadspeed 55', 'speed 80', 'rate 60', 'startsize 1', 'endsize 5', 'twist 30', 'jetlength 95', 'angles 0 0 0', 'rendercolor 255 10 10', 'SmokeMaterial particle/fire.vmt'):
		entity.add_output(output)
	entity.call_input('TurnOn')
	
	global _smokestack
	_smokestack = entity
	
@Event('bomb_defused')
def bomb_defused(event):
	_smokestack.add_output('rendercolor 10 10 255')
	
	origin = _smokestack.origin
	index = _tick_model.index
	recipients = RecipientFilter()
	for t in range(0, 3):
		temp_entities.beam_ring_point(recipients, t, origin, 20, 200, index, index, 0, 255, 1, 8, 1, 1, 10, 10, 255, 255, 1, 0)