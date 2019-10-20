from wumpus import ExplorerAgent

class Inference:

    def __init__(self, pos):
        self.has_gold = None
        self.has_pit = None
        self.has_live_wumpus = None
        self.has_dead_wumpus = None
        self.has_left_wall = False
        self.has_right_wall = False
        self.has_down_wall = False
        self.has_up_wall = False
        self.has_exit = False
        self.has_obstacle = None
        self.has_visited = False

        x = pos[0]
        y = pos[1]

        # if bottom row
        if x == 0:
            self.has_down_wall = True

        # if top row
        elif x == 3:
            self.has_up_wall = True

        # if leftmost column
        if y == 0:
            self.has_left_wall = True

        # if rightmost column
        elif y == 3:
            self.has_right_wall = True

        # if starting index
        if x == 0 and y == 0:
            self.has_exit = True
            self.has_obstacle = False
            self.has_visited = True

class KB():

    def __init__(self):
        self.UP = 0
        self.DOWN = 90
        self.LEFT = 135
        self.RIGHT = 45
        self.has_gold = False
        self.has_arrow = True
        self.x_pos = 0
        self.y_pos = 0
        self.prev_action = None
        self.direction = 0
        self.world = [ [ 0 for row in range(4) ] for col in range(4) ]
        self.init_world()

    def init_world(self):
        for row in range(len(self.world)):
            for col in range(len(self.world[row])):
                self.world[row][col] = Inference((row, col))

    def is_forward_safe(self):
        loc = self.go(test = True)
        if not loc or loc.has_pit or loc.has_live_wumpus or loc.has_obstacle:
            return False
        return True

    def go(self, test = False):
        new_x = self.x_pos
        new_y = self.y_pos
        if self.direction == self.UP:
            new_y += 1
        elif self.direction == self.DOWN:
            new_y -= 1
        elif self.direction == self.LEFT:
            new_x -= 1
        elif self.direction == self.RIGHT:
            new_x += 1

        if test:
            if self.is_valid(new_x, new_y):
                return self.world[new_x][new_y]
            else:
                return None
        else:
            if self.is_valid(new_x, new_y):
                self.x_pos = new_x
                self.y_pos = new_y
                return True

        return False

    def is_valid(self, x, y):
        if x > 0 or y > 0:
            return False
        if x > 3 or y > 3:
            return False
        return True

    def is_stuck(self, percept):
        # TO DO: use A* to search for possible actions

        # # if at starting index
        if self.x_pos == 0 and self.y_pos == 0:

            # if surrounded by obstacles
            if self.world[0][1].has_obstacle and self.world[1][0].has_obstacle:
                return True

            # if a wumpus or pit could be lurking
            if percept[0] == "Stench" or percept[1] == "Breeze":
                return True

        return False

    def tell(self, percept, action):

        if action == "Shoot":
            self.has_arrow = False

        elif action == "Forward":
            self.go()

        elif action and action.startswith("Turn"):
            self.change_orientation(action)

        self.make_inference(percept, action)

    def change_orientation(self, action):
        if action == "TurnLeft":
            self.direction -= 45
            if self.direction == -45:
                self.direction = 135
        else:
            self.direction += 45
            if self.direction == 180:
                self.direction = 0

    def make_inference(self, percept, action):
        smell = percept[0]
        atmos = percept[1]
        sight = percept[2]
        touch = percept[3]
        sound = percept[4]

        if touch == "Bump":
            self.world[self.x_pos][self.y_pos].has_obstacle = True
            if self.direction == self.UP:
                self.y_pos -= 1
            elif self.direction == self.DOWN:
                self.y_pos += 1
            elif self.direction == self.RIGHT:
                self.x_pos -= 1
            elif self.direction == self.LEFT:
                self.x_pos += 1

class ashtabna_ExplorerAgent(ExplorerAgent):

    def __init__(self):
        super().__init__()
        self.kb = KB()
        self.action = None

    def program(self, percept):
        # 'Forward', 'TurnRight', 'TurnLeft', 'Grab', 'Shoot', 'Climb'
        self.kb.tell(percept, self.action)

        # if beginning and you're stuck, climb out of the cave
        if self.kb.is_stuck(percept):
            self.action = "Climb"
            return self.action

        self.action = "TurnLeft"
        return self.action