import random
from loguru import logger

from dcss.actions.command import Command
from dcss.agent.base import BaseAgent
from dcss.state.game import GameState
from dcss.actions.action import Action
from dcss.state.menu import Menu

from dcss.actions.menuchoice import MenuChoiceMapping, MenuChoice

from dcss.websockgame import WebSockGame
from dcss.connection.config import WebserverConfig


class coeyFeatureAgent(BaseAgent):
    # coeyFeatureAgent.py is a basic agent meant to do simple planned feature-based exploration of the custom sprint levels.

    def __init__(self):
        super().__init__()
        self.gamestate = None
        self.turn = None
        self.msgList = None
        # Temporary features dictionary, mapping key strings to feature value ints
        self.features = {
            "stairDescend": 0,
            "exampleFeature": 132
        }
        self.commandQueue = []

    def get_action(self, gamestate: GameState):
        self.gamestate = gamestate
        self.turn = gamestate.get_current_game_turn()

        # Problem here: messages only has the key for the turn if some text appears. Keycode error if not.
        # Solution would be to try/catch the error. On fail, I know there's no text so go to a default.
        # - May need to revisit in future if this bug gets fixed.
        try: # need to check if this exists
            self.msgList = self.gamestate.messages[self.turn]
        except KeyError:
            self.msgList = None

        menu_id = self.gamestate.get_current_menu()

        # Queued up actions go first (such as accessing specific menu elements). All must be atomic in turn amount
        if(len(self.commandQueue) != 0):
            # print("\nCommandQueue: " + str(self.commandQueue))
            return self.commandQueue.pop(0) # returns first command in list and prepares next
        elif(menu_id != Menu.NO_MENU):
                menu_actions = MenuChoiceMapping.get_possible_actions_for_current_menu(menu_id)
                return random.choice(menu_actions)
        else:
                # Takeover method for agent to go down to next floor. TEMPORARY
                '''
                    The implementation I'm using for this method is to access the map-search menu
                    and having it auto-scroll to a staircase down and directly traveling to it.
                    
                    In user key inputs, this would be shift+x, >, ENTER. Followed by > to descend. 
                     Command.EXAMINE_LEVEL_MAP,, Command.TRAVEL_STAIRCASE_DOWN
                    Possible Problems:
                    - Need to account for possible monster interception.
                    - If staircase inaccessible for any reason.
                    - Optimization for which stairs to take. 
                '''
               # if (self.features["stairDescend"] == 1):
               #     print("Agent Done for now. WAITING")
               #     return Command.WAIT_1_TURN
                    # fight if see monster on the way, otherwise beeline to stairs.
                    # how to find stairs? Use cell data's self.has_stairs_down
                # Only run if messages came up at all. Note: These are temporary. Implement features here
                if (self.msgList != None):
                    if (self.features["stairDescend"] and str(self.msgList[len(self.msgList)-1]) == "There is a stone staircase leading down here."):
                        return Command.TRAVEL_STAIRCASE_DOWN
                    elif (str(self.msgList[len(self.msgList)-1]) == "You climb downwards."):
                        self.features["stairDescend"] = 0
                        return Command.AUTO_EXPLORE
                    # Go through the messages and if see "Done exploring." then run method to descend stairs.
                    elif (str(self.msgList[len(self.msgList)-1]) == "Done exploring."):
                        # print("Insert action sequence to leave floor here.")
                        # Plan: set Feature variable for some stairDescend to high, making it descend
                        self.features["stairDescend"] = 1
                        # Instead of previous plan, fill command queue to traverse to correct spot.
                        self.commandQueue.append(Command.EXAMINE_LEVEL_MAP) # access menu
                        self.commandQueue.append(Command.TRAVEL_STAIRCASE_DOWN) # in menu
                        self.commandQueue.append(Command.ENTER_KEY) # exit menu
                        return Command.WAIT_1_TURN
                    # If see "No target in view!", auto explore.
                    elif (str(self.msgList[len(self.msgList)-1]) == "No target in view!"):
                        print("Continue to explore.")
                        return Command.AUTO_EXPLORE

                # Default to fight if above are false.
                test_commands = [Command.AUTO_FIGHT]
                return random.choice(test_commands)


if __name__ == "__main__":
    my_config = WebserverConfig

    # Normal gameplay check
    # my_config.game_id = 'dcss-web-trunk'
    # my_config.delay = 0.1

    # Sprint gameplay check
    my_config.game_id = 'sprint-web-trunk'
    my_config.sprint_map_letter = 'a'
    my_config.delay = 0.3

    my_config.species = 'Minotaur'
    my_config.background = "Berserker"
    my_config.starting_weapon = "hand axe"

    # default loguru logging level is DEBUG
    # if you want to change this, uncomment the following, and replace INFO with your desired level
    # logger.remove()  # this removes all handlers, including the default one
    # logger.add(sys.stderr, level=config.LOG_LEVEL)  # stderr is the default one, so this is like replacing default
    # but with a different level

    # create game
    game = WebSockGame(config=my_config, agent_class=coeyFeatureAgent)
    game.run()

   

