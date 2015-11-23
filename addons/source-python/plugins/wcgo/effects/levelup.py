# ======================================================================
# >> IMPORTS
# ======================================================================

from wcgo.effects import models

from entities.entity import Entity
from entities.helpers import index_from_pointer
from listeners.tick import tick_delays

_tick_model = models['effects/yellowflare.vmt']

def level_up(player):
    player.client_command('play */source-python/wcs/levelup.mp3')
    pointer = player.give_named_item('env_smokestack', 0, None, False)
    entity = Entity(index_from_pointer(pointer))

    for output in ('basespread 10', 'spreadspeed 60', 'initial 0', 'speed 105',
        'rate 50', 'startsize 7', 'endsize 2', 'twist 0', 'jetlength 100',
        'angles 0 0 0', 'rendermode 18', 'renderamt 100',
        'rendercolor 255 255 3', 'SmokeMaterial effects/yellowflare.vmt'):
        entity.add_output(output)

    entity.call_input('TurnOn')
    entity.set_parent(player.pointer, -1)
    tick_delays.delay(2, entity.call_input, 'TurnOff')
    tick_delays.delay(2.1, entity.call_input, 'Kill')