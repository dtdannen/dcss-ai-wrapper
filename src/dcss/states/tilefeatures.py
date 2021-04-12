class TileFeatures:
    '''
    Contains feature data used per tile

    Returns a factored states representation of the tiles around the player:
        Example w/ radius of 1
        - 9 tiles including the player's current position and all adjacent tiles in every cardinal direction
        - each tile is represented as a factored states:
          <objType,monsterLetter,hasCorpse,hereBefore>
             * objType = 0 is empty, 1 is wall, 2 is monster
             * monsterLetter = 0-25 representing the alpha index of the first letter of mon name (0=a, etc)
             * hasCorpse = 0 if no edible corpse, 1 if edible corpse
             * hereBefore = 0 if first time player on this tile, 1 if player has already been here
    '''

    absolute_x = None
    absolute_y = None
    has_monster = 0
    last_visit = None  # None if never visited, 0 if currently here, otherwise >1 representing
    # number of actions executed since last visit