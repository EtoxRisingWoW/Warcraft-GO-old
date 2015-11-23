# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from itertools import cycle

# Source.Python
from messages import SayText2

wcs_adverts = (
    '>> \x03Warcraft: GO\x01: Type \x03"wcgo" \x01in chat or console to access the WCGO main menu.',
    '>> \x03Warcraft: GO\x01: Type \x03"playerinfo" \x01in chat to see other players WCGO info.',
    '>> \x03Warcraft: GO\x01: Type \x03"buyraces" \x01in chat to buy more races with gold.',
    '>> \x03Warcraft: GO\x01: Bind a key to \x03"ultimate" \x01to use a races ultimate.',
    '>> \x03Warcraft: GO\x01: Bind keys to \x03"ability 1" \x01and \x03"ability 2" \x01to use races abilities.',
)

adverts = cycle(map(SayText2, wcs_adverts))

def send_advert():
    next(adverts).send()