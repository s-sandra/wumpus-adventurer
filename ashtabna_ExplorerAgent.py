from wumpus import ExplorerAgent

class Inference:

    def __init__(self, pos):
        self.has_gold = None
        self.has_pit = None
        self.has_live_wumpus = None
        self.has_dead_wumpus = None
        self.has_left_wall = None
        self.has_right_wall = None
        self.has_down_wall = None
        self.has_up_wall = None
        self.has_exit = None
        self.has_obstacle = None

        x = pos[0]
        y = pos[1]

        # if starting index
        if x == 0 and y == 0:
            self.has_exit = True
            self.has_left_wall = True
            self.has_right_wall = False
            self.has_up_wall = False
            self.has_down_wall = True
            self.has_obstacle = False

        # if upper left corner
        elif x == 0 and y == 3:
            self.has_exit = False
            self.has_left_wall = True
            self.has_right_wall = False
            self.has_up_wall = True
            self.has_down_wall = False

        # if upper right corner
        elif x == 3 and y == 3:
            self.has_exit = False
            self.has_left_wall = False
            self.has_right_wall = True
            self.has_up_wall = True
            self.has_down_wall = False

        # if lower right corner
        elif x == 3 and y == 0:
            self.has_exit = False
            self.has_left_wall = False
            self.has_right_wall = True
            self.has_up_wall = False
            self.has_down_wall = True

class KB():

    def __init__(self):
        self.has_gold = False
        self.has_arrow = True
        self.position = (0, 0)
        self.world = [4][4]
        self.world[0][0] = Inference(self.position)

    def isPit(self, loc):
        return self.world[loc].hasPit

    def tell(self, x, y, percepts):
        pass


class yourUmwId_ExplorerAgent(ExplorerAgent):

    def __init__(self):
        super().__init__()
        self.kb = KB()

    def program(self, percept):
        smell = percept[0]
        atmos = percept[1]
        sight = percept[2]
        touch = percept[3]
        sound = percept[4]
        # 'Forward', 'TurnRight', 'TurnLeft', 'Grab', 'Shoot', 'Climb'