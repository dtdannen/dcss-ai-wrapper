from dcss.state.game import GameState


class BaseAgent:
    def __init__(self):
        pass

    def get_action(self, gamestate: GameState):
        raise NotImplementedError()

    def requesting_start_new_game(self):
        """
        This function enables the agent class to decide to start a new game. By default this is false,
        and subclasses of BaseAgent should implement this function to return True whenever a new game should begin.
        This function is especially helpful when you have some arbitrary criteria for which you want an agent to stop.
        """
        return False
