'''
CPSC 415 -- Homework #4, Wumpus World KB Agent
Sandra Shtabnaya, University of Mary Washington, fall 2019
'''
from wumpus import ExplorerAgent
import numpy as np
import queue

UP = 0
DOWN = 90
LEFT = 135
RIGHT = 45

class Inference:

    def __init__(self, pos):
        self.has_gold = None
        self.has_pit = None
        self.has_breeze = None
        self.has_stench = None
        self.has_live_wumpus = None
        self.has_dead_wumpus = None
        self.has_exit = False
        self.has_obstacle = None
        self.has_visited = False

        self.x_pos = pos[0]
        self.y_pos = pos[1]

        # if starting index
        if self.x_pos == 0 and self.y_pos == 0:
            self.has_exit = True
            self.has_pit = False
            self.has_obstacle = False
            self.has_visited = True
            self.has_gold = False
            self.has_live_wumpus = False
            self.has_dead_wumpus = False

class KB():

    def __init__(self):
        self.agent = AgentState()
        # self.prev_action = None
        self.world = [ [ 0 for row in range(4) ] for col in range(4) ]
        self.init_world()

    def init_world(self):
        for row in range(len(self.world)):
            for col in range(len(self.world[row])):
                self.world[row][col] = Inference((row, col))

    def get_state(self):
        return self.agent

    def get(self, x, y):
        if self.is_valid(x, y):
            return self.world[x][y]

    def get_location(self):
        return self.agent.get_location()

    def get_starting_loc(self):
        return self.world[0][0]

    def has_arrow(self):
        return self.agent.has_arrow

    def has_wumpus(self, x, y):
        if self.is_valid(x, y):
            loc = self.world[x][y]
            if loc.has_live_wumpus:
                return True
            else:
                return False
        return None

    def is_safe(self, x, y):
        if self.is_valid(x, y):
            loc = self.world[x][y]

        if not loc or loc.has_pit or loc.has_live_wumpus or loc.has_obstacle:
            return False
        return True

    def is_visited(self, x, y):
        loc = None
        if self.is_valid(x, y):
            loc = self.world[x][y]

        if loc and loc.has_visited:
            return True
        return False

    def is_valid(self, x, y):
        if x < 0 or y < 0:
            return False
        if x > 3 or y > 3:
            return False
        if self.world[x][y].has_obstacle:
            return False
        return True

    def tell(self, percept, action):
        loc = self.world[self.agent.x_pos][self.agent.y_pos]

        if action == "Shoot":
            self.has_arrow = False

        elif action == "Grab" and loc.has_gold:
            self.has_gold = True

        elif action == "Forward":
            self.agent.go(self.agent.direction)

        elif action and action.startswith("Turn"):
            self.agent.change_orientation(action)

        self.make_inference(percept, action)
        loc.has_visited = True

    def make_inference(self, percept, action):
        smell = percept[0]
        atmos = percept[1]
        sight = percept[2]
        touch = percept[3]
        sound = percept[4]
        curr_loc = self.world[self.agent.x_pos][self.agent.y_pos]

        if touch == "Bump":
            curr_loc.has_obstacle = True
            curr_loc.has_visited = True
            # movement unsuccessful. Change current location to previous location
            if self.direction == UP:
                self.y_pos -= 1
            elif self.direction == DOWN:
                self.y_pos += 1
            elif self.direction == RIGHT:
                self.x_pos -= 1
            elif self.direction == LEFT:
                self.x_pos += 1

        if sight == "Glitter":
            curr_loc.has_gold = True

        if sound == "Scream" and action == "Shoot":
            wumpus_loc = self.agent.go(self.direction, test = True)
            wumpus_loc.has_dead_wumpus = True
            for row in range(len(self.world)):
                for col in range(len(self.world[row])):
                    self.world[row][col].has_live_wumpus = False

        directions = [LEFT, RIGHT, UP, DOWN]

        for direction in directions:
            state = self.agent.go(direction, test=True)
            loc = self.world[state.x_pos][state.y_pos]
            if loc:
                if atmos == "Breeze":
                    curr_loc.has_breeze = True
                    if loc.has_pit == "Maybe":
                        loc.has_pit = True
                    elif not loc.has_visited:
                        loc.has_pit = "Maybe"
                else:
                    if not loc.has_visited:
                        loc.has_pit = False

                if smell == "Stench":
                    curr_loc.has_stench = True
                    if loc.has_live_wumpus == "Maybe":
                        loc.has_live_wumpus = True
                    elif not loc.has_visited:
                        loc.has_live_wumpus = "Maybe"
                else:
                    if not loc.has_visited:
                        loc.has_live_wumpus = False
                        loc.has_dead_wumpus = False

class AgentState():
    def __init__(self, x = 0, y = 0, d = 0):
        self.direction = d
        self.has_gold = False
        self.has_arrow = True
        self.x_pos = x
        self.y_pos = y

    def __eq__(self, other):
        if self.x_pos == other.x_pos and self.y_pos == self.other and self.direction == other.direction:
            return True
        return False

    def __hash__(self):
        return hash((self.x_pos, self.y_pos, self.direction))

    def get_location(self):
        return (self.x_pos, self.y_pos)

    def change_orientation(self, action, test=False):
        orientation = self.direction
        if action == "TurnLeft":
            orientation -= 45
            if orientation == -45:
                orientation = 135
        else:
            orientation += 45
            if orientation == 180:
                orientation = 0
        if test:
            return orientation
        self.direction = orientation

    def go(self, direction, test = False):
        new_x = self.x_pos
        new_y = self.y_pos
        if direction == UP:
            new_y += 1
        elif direction == DOWN:
            new_y -= 1
        elif direction == LEFT:
            new_x -= 1
        elif direction == RIGHT:
            new_x += 1

        if test:
            return AgentState(new_x, new_y, self.direction)
        else:
            self.x_pos = new_x
            self.y_pos = new_y

        return None

class ashtabna_ExplorerAgent(ExplorerAgent):

    def __init__(self):
        super().__init__()
        self.kb = KB()
        self.action = None
        self.plan = [] # stores a list of actions
        self.start = (0, 0)
        self.position = self.start

    """The main body of the agent program constructs a plan based on a decreasing priority of goals. First, if there is a glitter, the program constructs a plan to 
    grab the gold, follow a route back to the initial location, and climb out of the cave. Otherwise, if there is no current plan, the program plans a route 
    to the closest safe square that it has not visited yet, making sure the route goes through only safe squares. Route planning is done with A∗ search, not with 
    ASK. If there are no safe squares to explore, the next step—if the agent still has an arrow—is to try to make a safe square by shooting at one of the possible 
    wumpus locations. These are determined by asking where ASK(KB,¬Wx,y) is false—that is, where it is not known that there is not a wumpus. The function 
    PLAN-SHOT (not shown) uses PLAN-ROUTE to plan a sequence of actions that will line up this shot. If this fails, the program looks for a square to 
    explore that is not provably unsafe—that is, a square for which ASK(KB,¬OKt x,y) returns false. If there is no such square, then the mission is 
    impossible and the agent retreats to [1, 1] and climbs out of the cave. """

    def program(self, percept):
        self.kb.tell(percept, self.action)
        self.position = self.kb.get_location()
        self.action = "Forward" #random.choice(self.possible_actions)

        visited_safe_locs = []
        unvisited_safe_locs = []
        possible_wumpus_locs = []

        for row in range(4):
            for col in range(4):
                if self.kb.is_visited(row, col):
                    if self.kb.is_safe(row, col):
                        visited_safe_locs.append((row, col))
                else:
                    unvisited_safe_locs.append((row, col))
                    if self.kb.has_wumpus(row, col):
                        possible_wumpus_locs.append((row, col))

        if percept[2] == "Glitter":
            self.action = "Grab"
            self.goal = "Climb"
            route = self.make_plan([self.start], visited_safe_locs)
            self.plan.extend(route)
            self.plan.append("Climb")
            return self.action

        if not self.plan:
            plan = self.make_plan(unvisited_safe_locs, visited_safe_locs)
            self.plan = plan # is empty if no safe plan

        # if there is no safe route, try to shoot wumpus
        if not self.plan and self.kb.has_arrow():
            print("We can try to kill a wumpus!")
            for loc in possible_wumpus_locs:
                row = loc.x_pos
                col = loc.y_pos

        # if there is still no plan, climb out of cave
        if not self.plan:
            plan = self.make_plan([self.start], visited_safe_locs)
            plan.append("Climb")
            self.plan = plan

        action = self.plan.pop(0)
        print("I'm going to " + action)
        return action

    def get_valid_actions(self, location):
        actions = ["TurnLeft", "TurnRight", "Forward"]

        # if you can't go right
        if location.direction == RIGHT and not location.go(RIGHT, test = True):
            actions.remove("Forward")

        # if you can't go left
        if location.direction == LEFT and not location.go(LEFT, test = True):
            actions.remove("Forward")

        # if you can't go up
        if location.direction == UP and not location.go(UP, test = True):
            actions.remove("Forward")

        # if you can't go down
        if location.direction == DOWN and not location.go(DOWN, test = True):
            actions.remove("Forward")

        return actions

    def take_action(self, state, action):
        if action == "Forward":
            return state.go(state.direction, test = True)
        elif action.startswith("Turn"):
            state.change_orientation(action)
        return state

    def get_distance(self, loc, dest):
        return abs(loc[0] - dest[0]) + abs(loc[1] - dest[1])

    def make_plan(self, dest, world):
        frontier = queue.PriorityQueue()
        cost = np.inf
        path = []
        explored = {} # stores best paths to all locations
        goal = dest
        curr_state = self.kb.get_state()
        frontier.put((curr_state, 0))
        COST = 1
        STATE = 0
        explored[curr_state] = ["Grab"]

        'frontier = (state, cost)'
        'explored = state : "TurnLeft", "Forward"'

        # while there are locations to expand
        while not frontier.empty() and frontier.queue[0][COST] < cost:
            state = frontier.get()[STATE]
            actions = self.get_valid_actions(state)

            # loops through all squares connected to shortest square
            for action in actions:
                if not explored[state]:
                    frontier_path = [action]
                    frontier_cost = 1
                else:
                    frontier_path = explored[state] + [action]
                    frontier_cost = len(frontier_path)
                result = self.take_action(state, action)
                loc = state.get_location()
                allowed = result.get_location() in world
                new = loc not in explored.keys()
                # shorter = frontier_cost < len(explored[loc])

                # if this square hasn't been explored yet or we encountered a shorter path to this explored square
                if result.get_location() in world and (state not in explored.keys() or frontier_cost < len(explored[state])):
                    frontier.put((result, frontier_cost + self.get_distance(loc, goal[0]))) # places shortest on frontier
                    explored[state] = frontier_path # marks city as explored

                    # if this city leads to goal and path to get there is shorter than current solution
                    if loc in goal and frontier_cost < cost:
                        path = frontier_path
                        cost = frontier_cost
        return path