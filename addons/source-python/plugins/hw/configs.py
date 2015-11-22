# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import os

# Source.Python
import players.entity


# ======================================================================
# >> CONFIGURATIONS
# ======================================================================

# List of admin's steamid's
admins = (
    'STEAM_1:0:120220385', # Predz
)


# Prefix needed for chat commands
chat_command_prefix = '!'


# (Relative) path to database file used by Hero-Wars
database_path = os.path.dirname(__file__) + '/players.db'


# Amounts of experience points gained from objectives
exp_values = {

    # Kill values
    'Kill': 30,
    'Headshot': 15,
    'Assist': 15,

    # Round values
    'Round Win': 30,
    'Round Loss': 15,

    # Bomb values
    'Bomb Plant': 15,
    'Bomb Plant Team': 5,
    'Bomb Explode': 25,
    'Bomb Explode Team ': 10,
    'Bomb Defuse': 30,
    'Bomb Defuse Team ': 15,

    # Hostage values
    'Hostage Pick Up': 5,
    'Hostage Pick Up Team': 0,
    'Hostage Rescue': 25,
    'Hostage Rescue Team': 10
}

# Multiplier for experience gained upon events
__builtins__['exp_multiplier'] = 1

# Function for retrieving the experience event values
def _retrieve_exp_values(multiplier):
    return {k: v*multiplier for k, v in exp_values.items()}


# Amounts of gold gained from objectives
gold_values = {

    # Kill values
    'Kill': 2,
    'Assist': 1,

    # Round values
    'Round Win': 3,
    'Round Loss': 2
}


# Show messages for gold gain
show_gold_messages = True

# Shown message prefix ">> {prefix}: {message}"
message_prefix = 'Hero Wars'


# Starting heroes for when an user joins the server for the first time
# > Use class names for identifying the Hero classes
starting_heroes = (
    'Scourge',
)


# Hero category used when the category is not defined
default_hero_category = 'OTHERS'


# Item category used when the category is not defined
default_item_category = 'OTHERS'


# Items' default sell value's multiplier
item_sell_value_multiplier = 0.5


# Exp algorithm for required exp to level up
def exp_algorithm(level):
    return 100 + level * 20


# PlayerEntity class used as a super class of Hero-Wars's Player class
player_entity_class = players.entity.Player
