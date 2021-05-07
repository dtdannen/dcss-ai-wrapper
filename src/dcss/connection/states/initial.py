from dcss.connection.state import State


class Initial(State):
    def run(self):
        print("Waiting: Broadcasting cheese smell")

    def next(self, input):
        #if input == MouseAction.appears:
        #    return MouseTrap.luring
        #return MouseTrap.waiting
        pass