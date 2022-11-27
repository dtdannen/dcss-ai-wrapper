import autobahn.rawsocket.util
import os


class LocalConfig:
    """
        This configuration should be used when running DCSS in the terminal locally on the machine. Currently this
        has only been tested in Linux. It should work for Mac. Windows support is unknown.
    """
    socketpath = '127.0.0.1'  # do not change this
    server_ip = '127.0.0.1'
    server_port = '80'
    server_uri = None
    agent_name = 'midca'
    crawl_socketpath = '/home/dustin/Projects/crawl/crawl-ref/source/rcs/' + agent_name + ':crawl.sock'
    delay = 0.5


    @staticmethod
    def construct_server_uri():
        print("Looking for path: {}".format(LocalConfig.crawl_socketpath))
        if not os.path.exists(LocalConfig.crawl_socketpath):
            print("Could not find socket")
        else:
            print("  Found!")

        #LocalConfig.server_uri = autobahn.rawsocket.util.create_url(hostname="unix", port=LocalConfig.crawl_socketpath)
        LocalConfig.server_uri = LocalConfig.crawl_socketpath


class WebserverConfig:
    """
        This configuration should be used when running DCSS in webserver mode.
    """
    server_uri = 'ws://127.0.0.1:8080/socket'
    server_ip = '127.0.0.1'
    server_port = '8080'
    agent_name = 'midca'
    agent_password = 'midca'
    delay = 1  # delay in seconds to wait before sending the next message,
                 # decrease at your own risk. 0.5 and 1.0 have been known to be safe values

    # game_id is the type of game to play on the server
    #   'dcss-web-trunk'      - play trunk no seed
    #   'seeded-web-trunk'    - play a seeded version of the game
    #   'tut-web-trunk'       - play a tutorial
    #   'sprint-web-trunk'    - play a sprint
    game_id = 'tut-web-trunk'

    seed = 4675233756386659716

    tutorial_number = 1

    # this corresponds to the menu where you choose the map for the sprint
    # for example, Sprint I: "Red Sonja" is the letter 'a'
    sprint_map_letter = 'a'

    # start a new game after the last game ended
    auto_start_new_game = False

    # maximum number of actions to execute
    # -1 means infinite number of actions (i.e. don't stop agent after executing certain number of actions
    max_actions = -1

    # If this is true, and there is an existing game for the agent, delete the game and
    # start a new game
    always_start_new_game = False

    # any class that is in agent.py and is a subclass of Agent may be set as the ai_python_class
    ai_python_class = 'FastDownwardPlanningAgentTut1'

    # species selection configuration
    species = 'Minotaur'  # species name must match exactly to the string in the dcss menu after the dash, i.e. a hill orc is "Hill Orc"
    background = "Berserker"  # background name must match exactly to the string in the dcss menu after the dash
    starting_weapon = "hand axe"  # starting_weapon name must match exactly to the string in the dcss menu after the dash

    # whether or not to draw the map
    draw_map = False