from dcss.states.gamestate import GameState


class Agent:
    def __init__(self):
        pass

    def get_action(self, gamestate: GameState):
        raise NotImplementedError()

    def requesting_start_new_game(self):
        raise NotImplementedError()
