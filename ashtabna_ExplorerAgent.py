'''
CPSC 415 -- Homework #4, Wumpus World KB Agent
Sandra Shtabnaya, University of Mary Washington, fall 2019
'''

from wumpus import ExplorerAgent
import numpy as np
import queue

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

        x = pos[0]
        y = pos[1]

        # if starting index
        if x == 0 and y == 0:
            self.has_exit = True
            self.has_pit = False
            self.has_obstacle = False
            self.has_visited = True
            self.has_gold = False
            self.has_live_wumpus = False
            self.has_dead_wumpus = False

class KB():

    def __init__(self):
        self.UP = 0
        self.DOWN = 90
        self.LEFT = 135
        self.RIGHT = 45
        self.direction = 0

        self.has_gold = False
        self.has_arrow = True
        self.x_pos = 0
        self.y_pos = 0
        # self.prev_action = None
        self.world = [ [ 0 for row in range(4) ] for col in range(4) ]
        self.init_world()

    def init_world(self):
        for row in range(len(self.world)):
            for col in range(len(self.world[row])):
                self.world[row][col] = Inference((row, col))

    def get_position(self):
        return self.position

    def get_starting_loc(self):
        return self.world[0][0]

    def has_arrow(self):
        return self.has_arrow

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
        if self.is_valid(x, y):
            loc = self.world[x][y]

        if loc and loc.has_visited:
            return True
        return False

    def go(self, direction, test = False):
        new_x = self.x_pos
        new_y = self.y_pos
        if direction == self.UP:
            new_y += 1
        elif direction == self.DOWN:
            new_y -= 1
        elif direction == self.LEFT:
            new_x -= 1
        elif direction == self.RIGHT:
            new_x += 1

        if test:
            return self.get(new_x, new_y)
        else:
            if self.is_valid(new_x, new_y):
                self.x_pos = new_x
                self.y_pos = new_y
                return True

        return False

    def get(self, x, y):
        if self.is_valid(x, y):
            return self.world[x][y]
        else:
            return None

    def is_valid(self, x, y):
        if x > 0 or y > 0:
            return False
        if x > 3 or y > 3:
            return False
        return True

    def tell(self, percept, action):
        loc = self.world[self.x_pos][self.y_pos]

        if action == "Shoot":
            self.has_arrow = False

        elif action == "Grab" and loc.has_gold:
            self.has_gold = True

        elif action == "Forward":
            self.go(self.direction)

        elif action and action.startswith("Turn"):
            self.change_orientation(action)

        self.make_inference(percept, action)
        loc.has_visited = True

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
        curr_loc = self.world[self.x_pos][self.y_pos]

        if touch == "Bump":
            curr_loc.has_obstacle = True
            curr_loc.has_visited = True
            # movement unsuccessful. Change current location to previous location
            if self.direction == self.UP:
                self.y_pos -= 1
            elif self.direction == self.DOWN:
                self.y_pos += 1
            elif self.direction == self.RIGHT:
                self.x_pos -= 1
            elif self.direction == self.LEFT:
                self.x_pos += 1

        if sight == "Glitter":
            curr_loc.has_gold = True

        if sound == "Scream" and action == "Shoot":
            wumpus_loc = self.go(self.direction, test = True)
            wumpus_loc.has_dead_wumpus = True
            for row in range(len(self.world)):
                for col in range(len(self.world[row])):
                    self.world[row][col].has_live_wumpus = False

        directions = [self.LEFT, self.RIGHT, self.UP, self.DOWN]

        for direction in directions:
            loc = self.go(direction, test=True)
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

class ashtabna_ExplorerAgent(ExplorerAgent):

    def __init__(self):
        super().__init__()
        self.kb = KB()
        self.action = None
        self.plan = [] # stores a list of actions
        self.position = (0, 0)
        self.start = None

    """The main body of the agent program constructs a plan based on a decreasing priority of goals. First, if there is a glitter, the program constructs a plan to 
    grab the gold, follow a route back to the initial location, and climb out of the cave. Otherwise, if there is no current plan, the program plans a route 
    to the closest safe square that it has not visited yet, making sure the route goes through only safe squares. Route planning is done with A∗ search, not with 
    ASK. If there are no safe squares to explore, the next step—if the agent still has an arrow—is to try to make a safe square by shooting at one of the possible 
    wumpus locations. These are determined by asking where ASK(KB,¬Wx,y) is false—that is, where it is not known that there is not a wumpus. The function 
    PLAN-SHOT (not shown) uses PLAN-ROUTE to plan a sequence of actions that will line up this shot. If this fails, the program looks for a square to 
    explore that is not provably unsafe—that is, a square for which ASK(KB,¬OKt x,y) returns false. If there is no such square, then the mission is 
    impossible and the agent retreats to [1, 1] and climbs out of the cave. """

    def program(self, percept):
        # 'Forward', 'TurnRight', 'TurnLeft', 'Grab', 'Shoot', 'Climb'
        self.kb.tell(percept, self.action)
        self.position = self.kb.get_position()
        self.start = self.kb.get_starting_loc()
        self.action = "Forward" #random.choice(self.possible_actions)

        visited_safe_locs = []
        unvisited_safe_locs = []
        possible_wumpus_locs = []

        for row in range(4):
            for col in range(4):
                loc = self.kb.get(row, col)
                if self.kb.is_visited(row, col):
                    if self.kb.is_safe(row, col):
                        visited_safe_locs.append(loc)
                else:
                    unvisited_safe_locs.append(loc)
                    if self.kb.has_wumpus(row, col):
                        possible_wumpus_locs.append(loc)

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
                pass
                # row = loc.x_pos
                # col = loc.y_pos

        # if there is still no plan, climb out of cave
        if not self.plan:
            plan = self.make_plan([self.start], visited_safe_locs)
            self.plan = plan

        return self.plan.pop(0)

    def make_plan(self, purpose):
        frontier = queue.PriorityQueue()
        cost = np.inf
        path = [0]
        explored = {} # stores best paths to all cities
        goal = purpose
        loc = self.kb.get_location()
        frontier.put(loc)
        explored[loc] = 0
        COST = 0

        # while there are nodes to expand and the top of the frontier is cheaper than the solution
        while not frontier.empty() and frontier.queue[0][COST] < cost:
            shortest = frontier.get() # gets city on frontier with shortest distance
            short_city = shortest[CITY]

            # gets all cities connecting to shortest city
            connections = get_connecting_roads(atlas, shortest[1])

            # loops through all cities connected to shortest city
            for city, dist in connections.items():

                frontier_path = explored[short_city] + [city]
                frontier_cost = get_path_cost(frontier_path)

                # if this city hasn't been explored yet or we encountered a shorter path to this explored city
                if city not in explored.keys() or frontier_cost < get_path_cost(explored[city]):
                    frontier.put((frontier_cost + atlas.get_crow_flies_dist(city, goal), city)) # places city on frontier
                    explored[city] = frontier_path # marks city as explored

                    # if this city leads to goal and path to get there is shorter than current solution
                    if city == goal and frontier_cost < cost:
                        path = frontier_path
                        cost = frontier_cost

        return (path, cost)