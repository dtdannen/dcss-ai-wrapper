from dcss.states.gamestate import GameState


class Agent:
    def __init__(self):
        pass

    def get_action(self, gamestate: GameState):
        raise NotImplementedError()
