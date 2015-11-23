# ======================================================================
# >> IMPORTS
# ======================================================================

# Warcraft: GO
from wcgo.player import Player
from wcgo.player import PlayerIter

import wcgo.database
from wcgo.effects import level_up
from wcgo.entities import Hero

from wcgo.tools import get_messages
from wcgo.tools import find_element

from wcgo.menus import menus

from wcgo.heroes import *
from wcgo.items import *

import wcgo.configs as cfg

# Source.Python
from events import Event

from players.helpers import userid_from_playerinfo

from engines.server import engine_server

from cvars.public import PublicConVar

from plugins.info import PluginInfo

from translations.strings import LangStrings

from commands.client import ClientCommand

from messages import HintText, SayText2


# ======================================================================
# >> GLOBALS
# ======================================================================

# Plugin info
info = PluginInfo()
info.name = 'Warcraft: GO'
info.author = 'Mahi'
info.version = '0.6.1'
info.basename = 'wcgo'
info.variable = "{0}_version".format(info.basename)

# Public variable for plugin info
info.convar = PublicConVar(
    info.variable,
    info.version,
    0,
    "{0} Version".format(info.name)
)

# Experience Values
exp_values = cfg._retrieve_exp_values(cfg.exp_multiplier)

# Translation messages
exp_messages = get_messages(LangStrings('wcgo/exp'), HintText)
gold_messages = get_messages(LangStrings('wcgo/gold'), SayText2)
other_messages = get_messages(LangStrings('wcgo/other'), SayText2)


# ======================================================================
# >> FUNCTIONS
# ======================================================================

def load():
    """Setups the database upon sp load.

    Makes sure there are heroes on the server, restarts the game
    and setups the database file.

    Raises:
        NotImplementedError: When there are no heroes
    """

    heroes = Hero.get_subclasses()
    if not heroes:
        raise NotImplementedError('No heroes on the server.')
    if not cfg.starting_heroes:
        raise NotImplementedError('No starting heroes set.')
    for cid in cfg.starting_heroes:
        if not find_element(heroes, 'cid', cid):
            raise ValueError('Invalid starting hero cid: {0}'.format(cid))

    # Setup database
    wcgo.database.setup()

    # Restart the game
    engine_server.server_command('mp_restartgame 1\n')

    # Send a message to everyone
    other_messages['Plugin Loaded'].send()


def unload():
    """Save all unsaved data into database."""

    # Save each player's data into the database
    for player in PlayerIter():
        wcgo.database.save_player_data(player)

    # Commit and close
    wcgo.database.connection.commit()
    wcgo.database.connection.close()

    # Send a message to everyone
    other_messages['Plugin Unloaded'].send()


def give_gold(player, gold_key):
    """Gives player gold and sends him a message about it.

    Args:
        player: Player who to give gold to
        gold_key: Key used for finding the gold value and translation
    """

    if not cfg.show_gold_messages:
        return
    gold = cfg.gold_values.get(gold_key, 0)
    if gold > 0:
        player.gold += gold
        gold_messages[gold_key].send(player.index, gold=gold)


def give_exp(player, exp_key):
    """Gives player exp and sends him a message about it.

    Args:
        player: Player who to give exp to
        exp_key: Key used for finding the exp value and translation
    """

    exp = cfg.exp_values.get(exp_key, 0)
    if exp > 0:
        level = player.hero.level
        player.hero.exp += exp
        exp_messages[exp_key].send(player.index, exp=exp)
        if player.hero.level > level:
            hero_level_up(player)


def give_team_exp(player, exp_key):
    """Gives exp for player's teammates.

    Args:
        player: Player whose teammates to give exp to
        exp_key: Key used for finding the exp value and translation
    """

    # Give all his teammates exp
    for teammate in PlayerIter():
        if teammate.userid != player.userid:
            give_exp(teammate, exp_key)


# ======================================================================
# >> CLIENT COMMANDS
# ======================================================================

@ClientCommand(['buymenu'])
def client_command_buymenu(command, index):
    menus['Item Buy Categories'].send(index)
    return CommandReturn.BLOCK

@ClientCommand(['sellmenu', 'sell'])
def client_command_sellmenu(command, index):
    menus['Sell Items'].send(index)
    return CommandReturn.BLOCK

@ClientCommand('ultimate')
def client_command_ultimate(command, index):
    player = Player(index)
    player.hero.execute_skills('player_ultimate', player=player)
    return CommandReturn.BLOCK

@ClientCommand('showxp')
def client_command_showxp(command, index):
    player = Player(index)

    other_messages['Hero Status'].send(
        player.index,
        name=player.hero.name,
        level=player.hero.level,
        current=player.hero.exp,
        required=player.hero.required_exp
    )
    return CommandReturn.BLOCK

@ClientCommand(['wcsmenu', 'wcs'])
def client_command_menu(command, index):
    menus['Main'].send(index)
    return CommandReturn.BLOCK

# wcs_ability 1, wcs_ability 2, etc
@ClientCommand('ability')
def client_command_ability(command, index):
    ability_index = int(command.get_arg_string())
    player = Player(index)
    if len(player.hero.abilities) >= ability_index:
        ability = player.hero.abilities[ability_index-1]

        eargs = {
            'player': player
        }

        ability.execute_method('player_use', **eargs)
    return CommandReturn.BLOCK

@ClientCommand('wcsadmin')
def client_command_admin(command, index):
    player = Player(index)
    if player.steamid in cfg.admins:
        menus['Admin'].send(index)
    else:
        other_messages['Not Admin'].send(index)
    return CommandReturn.BLOCK

@ClientCommand('raceinfo')
def client_command_ability(command, index):
    player = Player(index)
    menu = _make_heroinfo(player.hero)
    menu.send(index)
    return CommandReturn.BLOCK

@ClientCommand('changerace')
def client_command_changerace(command, index):
    menus['Owned Heroes'].send(index)
    return CommandReturn.BLOCK

@ClientCommand('buyrace')
def client_command_buyrace(command, index):
    menus['Hero Buy Categories'].send(index)
    return CommandReturn.BLOCK

@ClientCommand('playerinfo')
def client_command_playerinfo(command, index):
    menus['Playerinfo Choose'].send(index)
    return CommandReturn.BLOCK

@SayCommand(['wcs', '!wcs'])
def say_command_menu(command, index, team):
    menus['Main'].send(index)
    return CommandReturn.BLOCK

@SayCommand(['wcsadmin', '!wcsadmin'])
def say_command_admin(command, index, team):
    player = Player(index)
    if player.steamid in cfg.admins:
        menus['Admin'].send(index)
    else:
        other_messages['Not Admin'].send(index)
    return CommandReturn.BLOCK

@SayCommand(['raceinfo', '!raceinfo'])
def say_command_raceinfo(command, index, team):
    player = Player(index)
    menu = _make_heroinfo(player.hero)
    menu.send(index)
    return CommandReturn.BLOCK

@SayCommand(['changerace', '!changerace'])
def say_command_changerace(command, index, team):
    menus['Owned Heroes'].send(index)
    return CommandReturn.BLOCK

@SayCommand(['buyraces', '!buyraces'])
def say_command_buyrace(command, index, team):
    menus['Hero Buy Categories'].send(index)
    return CommandReturn.BLOCK

@SayCommand(['playerinfo', '!playerinfo'])
def say_command_playerinfo(command, index, team):
    menus['Playerinfo Choose'].send(index)
    return CommandReturn.BLOCK

@SayCommand(['showxp', '!showxp'])
def say_command_showxp(command, index, team):
    player = Player(index)

    other_messages['Hero Status'].send(
        player.index,
        name=player.hero.name,
        level=player.hero.level,
        current=player.hero.exp,
        required=player.hero.required_exp
    )
    return CommandReturn.BLOCK

@SayCommand(['buymenu', 'buy', '!buymenu', '!buy'])
def say_command_buymenu(command, index, team):
    menus['Item Buy Categories'].send(index)
    return CommandReturn.BLOCK

@SayCommand(['sellmenu', 'sell', '!sellmenu', '!sell'])
def say_command_sellmenu(command, index, team):
    menus['Sell Items'].send(index)
    return CommandReturn.BLOCK


# ======================================================================
# >> GAME EVENTS
# ======================================================================

@Event('player_spawn')
def on_player_spawn(game_event):
    """Saves player's data.

    Also executes spawn skills and shows current exp/level progress.
    """

    # Get the player and his hero
    player = Player.from_userid(game_event.get_int('userid'))
    hero = player.hero

    # Show current exp and level
    other_messages['Hero Status'].send(
        player.index,
        name=hero.name,
        level=hero.level,
        current=hero.exp,
        required=hero.required_exp
    )

    # Execute spawn skills if the player's on a valid team
    if player.team > 1:
        hero.execute_skills('player_spawn', player=player)


@Event('player_death')
def on_player_death(game_event):
    """Executes kill, assist and death skills.

    Also gives exp from kill and assist.
    """

    # Get the defender
    defender = Player.from_userid(game_event.get_int('userid'))

    # Create the event arguments dict
    eargs = {
        'defender': defender,
        'attacker': None,
        'headshot': game_event.get_bool('headshot'),
        'weapon': game_event.get_string('weapon')
    }

    # Get the attacker and execute his and defender's skills
    attacker_id = game_event.get_int('attacker')
    if attacker_id and attacker_id != defender.userid:
        attacker = Player.from_userid(attacker_id)
        eargs['attacker'] = attacker
        attacker.hero.execute_skills('player_kill', **eargs)
        defender.hero.execute_skills('player_death', **eargs)

        # Give attacker exp from kill and headshot
        give_exp(attacker, 'Kill')
        if eargs['headshot']:
            give_exp(attacker, 'Headshot')

        # Give attacker gold from kill
        give_gold(attacker, 'Kill')

    # Else execute player_suicide skills
    else:
        defender.hero.execute_skills('player_suicide', **eargs)

    # Finally, remove defender's items
    for item in defender.hero.items:
        if not item.permanent:
            defender.hero.items.remove(item)


@Event('player_hurt')
def on_player_hurt(game_event):
    """Executes attack and defend skills."""

    # Get the defender
    defender = Player.from_userid(game_event.get_int('userid'))

    # Get the attacker
    attacker_id = game_event.get_int('attacker')
    if attacker_id and attacker_id != defender.userid:
        attacker = Player.from_userid(attacker_id)

        # Create event arguments dict
        eargs = {
            'defender': defender,
            'attacker': attacker,
            'damage': game_event.get_int('dmg_health'),
            'damage_armor': game_event.get_int('dmg_armor'),
            'weapon': game_event.get_string('weapon')
        }

        # Execute attacker's and defender's skills
        attacker.hero.execute_skills('player_attack', **eargs)
        defender.hero.execute_skills('player_defend', **eargs)


@Event('player_jump')
def on_player_jump(game_event):
    """Executes jump skills."""

    player = Player.from_userid(game_event.get_int('userid'))
    player.hero.execute_skills('player_jump', player=player)


@Event('player_say')
def on_player_say(game_event):
    """Executes ultimate skills and opens the menu."""

    # Get the player and the text
    player = Player.from_userid(game_event.get_int('userid'))
    text = game_event.get_string('text')

    # Finally, execute hero's player_say skills
    player.hero.execute_skills('player_say', player=player, text=text)


@Event('round_end')
def on_round_end(game_event):
    """Give exp from round win and loss.

    Also executes round_end skills.
    """

    # Get the winning team
    winner = game_event.get_int('winner')

    # Loop through all the players
    for player in PlayerIter():

        # Give player win exp and gold
        if player.team == winner:
            give_exp(player, 'Round Win')
            give_gold(player, 'Round Win')

        # Or loss exp and gold
        else:
            give_exp(player, 'Round Loss')
            give_gold(player, 'Round Loss')

        # Execute hero's round_end skills
        player.hero.execute_skills('round_end', player=player, winner=winner)


@Event('round_start')
def on_round_start(game_event):
    """Executes round_start skills."""

    global exp_values
    exp_values = cfg._retrieve_exp_values(cfg.exp_multiplier)

    for player in PlayerIter():
        player.hero.execute_skills(
            'round_start', player=player, winner=game_event.get_int('winner'))


@Event('bomb_planted')
def on_bomb_planted(game_event):
    """Give exp from bomb planting.

    Also executes bomb_planted skills.
    """

    player = Player.from_userid(game_event.get_int('userid'))
    give_exp(player, 'Bomb Plant')
    give_team_exp(player, 'Bomb Plant Team')
    player.hero.execute_skills('bomb_planted', player=player)


@Event('bomb_exploded')
def on_bomb_exploded(game_event):
    """Give exp from bomb explosion.

    Also executes bomb_exploded skills.
    """

    player = Player.from_userid(game_event.get_int('userid'))
    give_exp(player, 'Bomb Explode')
    give_team_exp(player, 'Bomb Explode Team')
    player.hero.execute_skills('bomb_exploded', player=player)


@Event('bomb_defused')
def on_bomb_defused(game_event):
    """Give exp from bomb defusion.

    Also executes bomb_defused skills.
    """

    player = Player.from_userid(game_event.get_int('userid'))
    give_exp(player, 'Bomb Defuse')
    give_team_exp(player, 'Bomb Defuse Team')
    player.hero.execute_skills('bomb_defused', player=player)


@Event('hostage_follows')
def on_hostage_follows(game_event):
    """Give exp from hostage pick up.

    Also executes hostage_follows skills.
    """

    player = Player.from_userid(game_event.get_int('userid'))
    give_exp(player, 'Hostage Pick Up')
    give_team_exp(player, 'Hostage Pick Up Team')
    player.hero.execute_skills('hostage_follows', player=player)


@Event('hostage_rescued')
def on_hostage_rescued(game_event):
    """Give exp from hostage rescue.

    Also executes hostage_rescued skills.
    """

    player = Player.from_userid(game_event.get_int('userid'))
    give_exp(player, 'Hostage Rescue')
    give_team_exp(player, 'Hostage Rescue Team')
    player.hero.execute_skills('hostage_rescued', player=player)


def hero_level_up(player):
    """Sends hero's status to player and opens current hero menu.

    Also executes hero_level_up skills.
    """
    hero = player.hero

    # Send hero's status via chat
    other_messages['Hero Status'].send(
        index,
        name=hero.name,
        level=hero.level,
        current=hero.exp,
        required=hero.required_exp
    )

    # Open current hero info menu (Kamiqawa, what?) to let the player
    # spend skill points
    menus['Current Hero'].send(index)

    # Execute player's skills
    player.hero.execute_skills('hero_level_up', player=player, hero=hero)

    level_up(player)
