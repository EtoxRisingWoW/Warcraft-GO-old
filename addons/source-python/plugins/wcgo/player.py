﻿# ======================================================================
# >> IMPORTS
# ======================================================================

# Warcraft: GO from wcgo.database import save_player_data
from wcgo.database import load_player_data
from wcgo.database import save_hero_data

from wcgo.entities import Hero

from wcgo.tools import find_element

from wcgo.configs import starting_heroes
from wcgo.configs import player_entity_class

# Source.Python
from players.helpers import index_from_userid
from players import PlayerGenerator

from memory import make_object

from entities import TakeDamageInfo
from entities.hooks import EntityPreHook
from entities.hooks import EntityCondition
from entities.helpers import index_from_edict
from entities.helpers import index_from_pointer

from events import Event

from filters.iterator import _IterObject

from weapons.entity import Weapon


# ======================================================================
# >> GAME EVENTS
# ======================================================================

@Event('player_disconnect')
def on_player_disconnect(game_event):
    """Saves player's data upon disconnect."""

    userid = game_event.get_int('userid')
    player = Player.from_userid(userid)
    save_player_data(player)
    del Player._data[userid]


@Event('player_spawn')
def on_player_spawn(game_event):
    """Saves player's data upon spawning."""

    player = Player.from_userid(game_event.get_int('userid'))
    save_player_data(player)


# ======================================================================
# >> HOOKS
# ======================================================================

@EntityPreHook(EntityCondition.is_player, 'bump_weapon')
def _pre_bump_weapon(args):
    """
    Hooked to a function that is fired any time a weapon is
    requested to be picked up in game.
    """

    player_index = index_from_pointer(args[0])
    weapon_index = index_from_pointer(args[1])
    weapon = Weapon(weapon_index)
    player = Player(player_index)
    eargs = {'weapon': weapon, 'player': player}
    if weapon.classname in player.restrictions:
        player.hero.execute_skills('weapon_pickup_fail', **eargs)
        return False
    else:
        player.hero.execute_skills('weapon_pickup', **eargs)

@EntityPreHook(EntityCondition.is_player, 'buy_internal')
def _on_buy_internal(args):
    """
    Hooked to a function that is fired any time a weapon
    is purchased. (Stops bots from buying.)
    """
    player_index = index_from_pointer(args[0])
    player = Player(player_index)
    if player.playerinfo.is_fake_client() and len(player.restrictions) > 0:
        return 0

@EntityPreHook(EntityCondition.is_player, 'on_take_damage')
def _pre_on_take_damage(args):
    """
    Hooked to a function that is fired any time an
    entity takes damage.
    """

    player_index = index_from_pointer(args[0])
    info = make_object(TakeDamageInfo, args[1])
    defender = Player(player_index)
    attacker = None if not info.attacker else Player(info.attacker)
    eargs = {
        'attacker': attacker,
        'defender': defender,
        'info': info,
        'weapon': Weapon(
            index_from_inthandle(attacker.active_weapon)
            ).class_name if attacker and attacker.active_weapon != -1 else ''
    }
    if not player_index == info.attacker:
        defender.hero.execute_skills('player_pre_defend', **eargs)
        '''
        Added exception to check whether world caused damage.
        '''
        if attacker:
            attacker.hero.execute_skills('player_pre_attack', **eargs)


# ======================================================================
# >> CLASSES
# ======================================================================

class PlayerIter(_IterObject):
    """Player iterate class."""

    @staticmethod
    def iterator():
        """Iterate over all Player objects."""
        # Loop through all players on the server
        for edict in PlayerGenerator():

            # Yield the Player instance for the current edict
            yield Player(index_from_edict(edict))


class Player(player_entity_class):
    """Player class for Hero-Wars related activity and data.

    Attributes:
        gold: Player's Hero-Wars gold, used to purchase heroes and items
        hero: Player's hero currently in use
        heroes: List of owned heroes
    """

    _data = {}

    @classmethod
    def from_userid(cls, userid):
        """Returns a Player instance from an userid.

        Args:
            userid: Userid of the player
        """

        return cls(index_from_userid(userid))

    def __init__(self, index):
        """Initializes a new player instance.

        Args:
            index: Index of the player
        """

        super().__init__(index)

        # Create player's data dict
        if self.userid not in Player._data:
            Player._data[self.userid] = {
                'gold': 0,
                'hero': None,
                'heroes': [],
                'restrictions': set()
            }

            # Load player's data
            load_player_data(self)

            # Make sure the player gets his starting heroes
            heroes = Hero.get_subclasses()
            for cid in starting_heroes:
                hero_cls = find_element(heroes, 'cid', cid)
                if hero_cls and not find_element(self.heroes, 'cid', cid):
                    self.heroes.append(hero_cls())

            # Make sure the player has a hero
            if not self.hero:
                self.hero = self.heroes[0]

    @property
    def gold(self):
        """Getter for player's Hero-Wars gold.

        Returns:
            Player's gold
        """

        return Player._data[self.userid]['gold']

    @gold.setter
    def gold(self, gold):
        """Setter for player's Hero-Wars gold.

        Raises:
            ValueError: If gold is set to a negative value
        """

        if gold < 0:
            raise ValueError('Attempt to set negative gold for a player.')
        Player._data[self.userid]['gold'] = gold

    @property
    def hero(self):
        """Getter for player's current hero.

        Returns:
            Player's hero
        """

        return Player._data[self.userid]['hero']

    @hero.setter
    def hero(self, hero):
        """Setter for player's current hero.

        Makes sure player owns the hero and saves his current hero to
        the database before switching to the new one.

        Args:
            hero: Hero to switch to

        Raises:
            ValueError: Hero not owned by the player
        """

        # Make sure player owns the hero
        if hero not in self.heroes:
            raise ValueError('Hero {cid} not owned by {steamid}.'.format(
                cid=hero.cid, steamid=self.steamid
            ))

        # Make sure the hero is different than player's current hero
        if hero == self.hero:
            return

        # If player has a current hero
        if self.hero:

            # Save current hero's data
            save_hero_data(self.steamid, self.hero)

            # Destroy current hero's items
            for item in self.hero.items:
                if not item.permanent:
                    self.hero.items.remove(item)

            # Slay the player
            self.client_command(self.edict, 'kill', True)

        # Change to the new hero
        Player._data[self.userid]['hero'] = hero

        # Reset current restrictions
        self.restrictions.clear()

    @property
    def heroes(self):
        """Getter for player's heroes.

        Returns:
            A list of player's heroes.
        """

        return Player._data[self.userid]['heroes']

    @property
    def restrictions(self):
        """Getter for player's restrictions.

        Returns:
            A set of player's restricted weapons
        """

        return Player._data[self.userid]['restrictions']

    @restrictions.setter
    def restrictions(self, restrictions):
        """Setter for player's restrictions."""

        self.restrictions.clear()
        self.restrictions.update(set(restrictions))
