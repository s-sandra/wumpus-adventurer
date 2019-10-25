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

def is_valid(x, y):
    if x < 0 or y < 0:
        return False
    if x > 3 or y > 3:
        return False
    # if self.world[x][y].has_obstacle:
    #     return False
    return True

class Inference:

    def __init__(self, pos):
        self.has_gold = None
        self.has_pit = None
        self.has_breeze = None
        self.has_stench = None
        self.has_live_wumpus = None
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

    def __repr__(self):
        return "Inference at {0}. Has Wumpus: {1} Has obstacle: {2} Has pit: {3}".format((self.x_pos, self.y_pos),
                                                                                         self.has_live_wumpus,
                                                                                         self.has_obstacle,
                                                                                         self.has_pit)


class KB():

    def __init__(self):
        self.agent = AgentState()
        # self.prev_action = None
        self.world = [[0 for row in range(4)] for col in range(4)]
        self.init_world()

    def init_world(self):
        for row in range(len(self.world)):
            for col in range(len(self.world[row])):
                self.world[row][col] = Inference((row, col))

    def get_state(self):
        return self.agent

    def get(self, x, y):
        if is_valid(x, y):
            return self.world[x][y]

    def get_location(self):
        return self.agent.get_location()

    def get_starting_loc(self):
        return self.world[0][0]

    def has_arrow(self):
        return self.agent.has_arrow

    def has_wumpus(self, x, y):
        if is_valid(x, y):
            loc = self.world[x][y]
            if loc.has_live_wumpus:
                return True
            else:
                return False
        return None

    def is_safe(self, x, y):
        if is_valid(x, y):
            loc = self.world[x][y]

        if not loc or loc.has_pit or loc.has_live_wumpus or loc.has_obstacle:
            return False
        return True

    def is_visited(self, x, y):
        loc = None
        if is_valid(x, y):
            loc = self.world[x][y]

        if loc and loc.has_visited:
            return True
        return False

    def tell(self, percept, action):
        loc = self.world[self.agent.x_pos][self.agent.y_pos]

        if action == "Shoot":
            self.has_arrow = False

        elif action == "Grab" and loc.has_gold:
            self.has_gold = True

        elif action == "Forward":
            self.agent.go(self.agent.direction)
            loc = self.world[self.agent.x_pos][self.agent.y_pos]

        elif action and action.startswith("Turn"):
            self.agent.change_orientation(action)

        self.make_inference(percept, action)
        loc.has_visited = True
        loc.has_obstacle = False

    def make_inference(self, percept, action):
        smell = percept[0]
        atmos = percept[1]
        sight = percept[2]
        touch = percept[3]
        sound = percept[4]
        curr_loc = self.world[self.agent.x_pos][self.agent.y_pos]

        if touch == "Bump":
            curr_loc.has_obstacle = True
            curr_loc.has_live_wumpus = False
            curr_loc.has_pit = False
            curr_loc.has_visited = True
            self.agent.undo() # movement unsuccessful. Change current location to previous location

        else:
            if sight == "Glitter":
                curr_loc.has_gold = True

            if sound == "Scream" and action == "Shoot":
                wumpus_loc = self.agent.go(self.agent.direction, test=True)
                wumpus_loc.has_live_wumpus = False
                for row in range(len(self.world)):
                    for col in range(len(self.world[row])):
                        self.world[row][col].has_live_wumpus = False

            directions = [LEFT, RIGHT, UP, DOWN]

            # make deductions for valid locations in all directions
            for direction in directions:
                state = self.agent.go(direction, test=True)

                # if valid location
                if state:
                    loc = self.world[state.x_pos][state.y_pos]
                    if atmos == "Breeze":
                        curr_loc.has_breeze = True
                        if loc.has_pit == "Maybe":
                            loc.has_pit = True
                        elif not loc.has_visited and loc.has_pit is None:
                            loc.has_pit = "Maybe"
                    else:
                        if loc.has_pit == "Maybe" or not loc.has_visited:
                            loc.has_pit = False

                    if smell == "Stench":
                        curr_loc.has_stench = True
                        if loc.has_live_wumpus == "Maybe":
                            loc.has_live_wumpus = True

                            # no other locations can have a wumpus
                            for row in range(len(self.world)):
                                for col in range(len(self.world[row])):
                                    if loc.has_live_wumpus != True:
                                        loc.has_live_wumpus = False

                        elif not loc.has_visited and loc.has_live_wumpus is None:
                            loc.has_live_wumpus = "Maybe"
                    else:
                        if loc.has_live_wumpus == "Maybe" or not loc.has_visited:
                            loc.has_live_wumpus = False


class AgentState():
    def __init__(self, x=0, y=0, d=0, c=0):
        self.direction = d
        self.has_gold = False
        self.has_arrow = True
        self.x_pos = x
        self.y_pos = y
        self.cost = c

    def __eq__(self, other):
        if self.x_pos == other.x_pos and self.y_pos == other.y_pos and self.direction == other.direction:
            return True
        return False

    def __hash__(self):
        return hash((self.x_pos, self.y_pos, self.direction))

    def __repr__(self):
        direction = self.get_direction()
        return "State at {0} facing {1}".format(self.get_location(), direction)

    def __lt__(self, other):
        return self.cost < other.cost

    def get_location(self):
        return (self.x_pos, self.y_pos)

    def get_direction(self):
        if self.direction == UP:
            return "up"
        elif self.direction == DOWN:
            return "down"
        elif self.direction == LEFT:
            return "left"
        elif self.direction == RIGHT:
            return "right"

    def change_orientation(self, action, test=False):
        orientation = self.direction
        if action == "TurnLeft":
            orientation -= 45
            if orientation == -45:
                orientation = 135
        elif action == "TurnLeft":
            orientation += 45
            if orientation == 180:
                orientation = 0
        if test:
            return AgentState(self.x_pos, self.y_pos, orientation)
        self.direction = orientation

    def reverse(self):
        self.direction += 90
        if self.direction >= 180:
            self.direction -= 180

    def go(self, direction, test=False):
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

        if is_valid(new_x, new_y):
            if test:
                return AgentState(new_x, new_y, direction)
            else:
                self.x_pos = new_x
                self.y_pos = new_y

        return None

    def undo(self):
        if self.direction == UP:
            self.y_pos -= 1
        elif self.direction == DOWN:
            self.y_pos += 1
        elif self.direction == RIGHT:
            self.x_pos -= 1
        elif self.direction == LEFT:
            self.x_pos += 1


class ashtabna_ExplorerAgent(ExplorerAgent):

    def __init__(self):
        super().__init__()
        self.kb = KB()
        self.action = None
        self.plan = []  # stores a list of actions
        self.start = AgentState(0, 0)
        self.position = self.start

    """If there are no safe squares to explore, the next step—if the agent still has an arrow—is to try to make a square safe by shooting at one of the possible 
    wumpus locations. These are determined by asking where ASK(KB,¬Wx,y) is false—that is, where it is not known that there is not a wumpus. The function 
    PLAN-SHOT (not shown) uses PLAN-ROUTE to plan a sequence of actions that will line up this shot. If this fails, the program looks for a square to 
    explore that is not provably unsafe—that is, a square for which ASK(KB,¬OKt x,y) returns false. If there is no such square, then the mission is 
    impossible and the agent retreats to [1, 1] and climbs out of the cave. """

    def program(self, percept):
        self.kb.tell(percept, self.action)
        self.position = self.kb.get_location()

        safe_locs = []
        unsafe_locs = []
        unvisited_safe_locs = []
        possible_wumpus_locs = []

        for row in range(4):
            for col in range(4):

                if self.kb.is_safe(row, col):
                    safe_locs.append(AgentState(row, col, UP))
                    safe_locs.append(AgentState(row, col, DOWN))
                    safe_locs.append(AgentState(row, col, LEFT))
                    safe_locs.append(AgentState(row, col, RIGHT))

                    if not self.kb.is_visited(row, col):
                        unvisited_safe_locs.append(AgentState(row, col, UP))
                        unvisited_safe_locs.append(AgentState(row, col, DOWN))
                        unvisited_safe_locs.append(AgentState(row, col, LEFT))
                        unvisited_safe_locs.append(AgentState(row, col, RIGHT))

                elif not self.kb.is_safe(row, col):
                    unsafe_locs.append(AgentState(row, col, UP))
                    unsafe_locs.append(AgentState(row, col, DOWN))
                    unsafe_locs.append(AgentState(row, col, LEFT))
                    unsafe_locs.append(AgentState(row, col, RIGHT))

                    if self.kb.has_wumpus(row, col):
                        possible_wumpus_locs.append(AgentState(row, col))

        # if treasure here, grab and plan shortest route to exit
        if percept[2] == "Glitter":
            self.action = "Grab"
            route = self.make_plan([self.start], safe_locs)
            self.plan.extend(route)
            self.plan.append("Climb")
            return self.action

        # if no treasure, plan shortest route to safe location
        if not self.plan:
            self.plan = self.make_plan(unvisited_safe_locs, safe_locs)

        # if there is no safe route, guess where wumpus is and shoot
        if not self.plan and self.kb.has_arrow():
            plan = self.plan_shot(possible_wumpus_locs, safe_locs)
            plan.append("Shoot")
            self.plan.extend(plan)

        # if there is no way to safely shoot wumpus
        if not self.plan:
            plan = self.make_plan(unsafe_locs, safe_locs)
            self.plan.extend(plan)

        # if there is still no plan, climb out of cave
        if not self.plan:
            plan = self.make_plan([self.start], safe_locs)
            plan.append("Climb")
            self.plan = plan

        self.action = self.plan.pop(0)
        print("I'm going to " + self.action)
        return self.action

    def get_valid_actions(self, location):
        actions = ["TurnLeft", "TurnRight", "Forward"]

        # if you can't go right
        if location.direction == RIGHT and not location.go(RIGHT, test=True):
            actions.remove("Forward")

        # if you can't go left
        if location.direction == LEFT and not location.go(LEFT, test=True):
            actions.remove("Forward")

        # if you can't go up
        if location.direction == UP and not location.go(UP, test=True):
            actions.remove("Forward")

        # if you can't go down
        if location.direction == DOWN and not location.go(DOWN, test=True):
            actions.remove("Forward")

        return actions

    def take_action(self, state, action):
        if action == "Forward":
            return state.go(state.direction, test=True)
        elif action.startswith("Turn"):
            return state.change_orientation(action, test=True)

    def get_distance(self, loc, dest):
        return abs(loc.x_pos - dest.x_pos) + abs(loc.y_pos - dest.y_pos)

    def plan_shot(self, wumpus_locs, world):
        shooting_locs = [] # positions from which agent can shoot at wumpus

        # compute all locations surrounding and facing wumpus
        for state in wumpus_locs:
            loc = state.get_location()
            row = loc[0]
            col = loc[1]
            wumpus = AgentState(row, col)

            directions = [UP, DOWN, LEFT, RIGHT]

            for direction in directions:
                pos = wumpus.go(direction, test=True)
                if pos:
                    pos.reverse()
                    shooting_locs.append(pos)

        return self.make_plan(shooting_locs, world)

    def is_allowed(self, loc, world):
        for room in world:
            if loc == room.get_location():
                return True
        return False

    def make_plan(self, dest, world):
        paths = []
        goals = dest
        curr_state = self.kb.get_state()

        # finds best path to all goal states
        for goal in goals:
            cost = np.inf
            path = []
            frontier = queue.PriorityQueue()
            explored = {}  # stores best paths to all states
            frontier.put(curr_state)
            explored[curr_state] = []

            # while there are locations to expand
            while not frontier.empty() and frontier.queue[0].cost < cost:
                state = frontier.get()
                loc = state.get_location()

                if state == goal:
                    return explored[state]

                actions = self.get_valid_actions(state)

                # loops through all squares connected to shortest square
                for action in actions:
                    frontier_path = explored[state] + [action]
                    frontier_cost = len(frontier_path)
                    result = self.take_action(state, action)
                    result_loc = result.get_location()

                    # if this square hasn't been explored yet or we encountered a shorter path to this explored square
                    if result in world and (result not in explored.keys() or frontier_cost < len(explored[result])):
                        path_cost = self.get_distance(result, goal) + frontier_cost
                        result.cost = path_cost
                        frontier.put(result)  # places shortest on frontier
                        explored[result] = frontier_path  # marks location as explored

                        # if this location leads to goal and path to get there is shorter than current solution
                        if result == goal and frontier_cost < cost:
                            path = frontier_path
                            cost = frontier_cost

            paths.append((path, cost))

        if paths:
            return min(paths, key = lambda t: t[1])[0]
        return paths
