'''
CPSC 415 -- Homework #4, Wumpus World KB Agent
Sandra Shtabnaya, University of Mary Washington, fall 2019
'''
from wumpus import ExplorerAgent
import numpy as np
import queue
from itertools import combinations

UP = 0
DOWN = 90
LEFT = 135
RIGHT = 45
PIT_PRIOR = 0.2 # the probability of a location having a pit
directions = [UP, DOWN, LEFT, RIGHT]

def is_valid(x, y):
    if x < 0 or y < 0:
        return False
    if x > 3 or y > 3:
        return False
    return True

class Inference:

    def __init__(self, pos):
        self.has_pit = None
        self.has_live_wumpus = None
        self.has_obstacle = None
        self.has_visited = False

        self.x_pos = pos[0]
        self.y_pos = pos[1]

        # if starting index
        if self.x_pos == 0 and self.y_pos == 0:
            # self.has_exit = True
            self.has_pit = False
            self.has_obstacle = False
            self.has_visited = True
            # self.has_gold = False
            self.has_live_wumpus = False

    def __repr__(self):
        return "Inference at {0}. Has Wumpus: {1} Has obstacle: {2} Has pit: {3}".format((self.x_pos, self.y_pos),
                                                                                         self.has_live_wumpus,
                                                                                         self.has_obstacle,
                                                                                         self.has_pit)

    def __eq__(self, other):
        return self.x_pos == other.x_pos and self.y_pos == other.y_pos

    def __hash__(self):
        return hash((self.x_pos, self.y_pos))

class KB():

    def __init__(self):
        self.agent = AgentState()
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

    def get_direction(self):
        return self.agent.direction

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

    def is_maybe_safe(self, x, y):
        if is_valid(x, y):
            loc = self.world[x][y]

        if loc.has_pit == "Maybe" or loc.has_live_wumpus == "Maybe":
            return True
        return False

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
            self.agent.has_arrow = False

        elif action == "Forward":
            self.agent.go(self.agent.direction)
            loc = self.world[self.agent.x_pos][self.agent.y_pos]

        elif action and action.startswith("Turn"):
            self.agent.change_orientation(action)

        self.make_inference(percept, action)
        loc.has_visited = True

        # if we thought there was a pit here, but there's not
        if loc.has_pit == "Maybe":
            loc.has_pit = False

    def make_inference(self, percept, action):
        smell = percept[0]
        atmos = percept[1]
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
            curr_loc.has_obstacle = False

            if action == "Shoot":
                shooting_loc = self.agent.go(self.agent.direction, test=True).get_location()
                shooting_loc = self.world[shooting_loc[0]][shooting_loc[1]]

                if sound == "Scream":
                    shooting_loc.has_pit = False
                    shooting_loc.has_obstacle = False
                    for row in range(len(self.world)):
                        for col in range(len(self.world[row])):
                            self.world[row][col].has_live_wumpus = False

                # if we shot at this location and didn't hear scream, no wumpus there
                else:
                    shooting_loc.has_live_wumpus = False

            # make deductions for valid locations in all directions
            for direction in directions:
                state = self.agent.go(direction, test=True)

                # if valid location
                if state:
                    loc = self.world[state.x_pos][state.y_pos]
                    if atmos == "Breeze":
                        curr_loc.has_breeze = True
                        if not curr_loc.has_visited and loc.has_pit == "Maybe":
                            loc.has_pit = True
                        elif not loc.has_visited and loc.has_pit is None:
                            loc.has_pit = "Maybe"
                    else:
                        if loc.has_pit == "Maybe" or not loc.has_visited:
                            loc.has_pit = False

                    if smell == "Stench":
                        curr_loc.has_stench = True
                        if not curr_loc.has_visited and loc.has_live_wumpus == "Maybe":
                            loc.has_live_wumpus = True
                            loc.has_pit = False
                            loc.has_obstacle = False

                            # no other locations can have a wumpus
                            for row in range(len(self.world)):
                                for col in range(len(self.world[row])):
                                    room = self.world[row][col]
                                    if room.has_live_wumpus != True:
                                        room.has_live_wumpus = False

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
        elif action == "TurnRight":
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
        if direction == UP or self.direction == UP and direction == "Forward":
            new_y += 1
            direction = UP
        elif direction == DOWN or self.direction == DOWN and direction == "Forward":
            new_y -= 1
            direction = DOWN
        elif direction == LEFT or self.direction == LEFT and direction == "Forward":
            new_x -= 1
            direction = LEFT
        elif direction == RIGHT or self.direction == RIGHT and direction == "Forward":
            new_x += 1
            direction = RIGHT

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
        self.goal = None
        self.position = self.start

    def program(self, percept):
        self.kb.tell(percept, self.action)
        self.position = self.kb.get_location()

        safe_locs = []
        unsafe_locs = []
        maybe_unsafe_locs = []
        unvisited_safe_locs = []
        possible_wumpus_locs = []

        for row in range(4):
            for col in range(4):
                for direction in directions:
                    location = AgentState(row, col, direction)
                    if self.kb.is_safe(row, col):
                        safe_locs.append(location)

                        if not self.kb.is_visited(row, col):
                            unvisited_safe_locs.append(location)
                    else:
                        unsafe_locs.append(location)

                if self.kb.has_wumpus(row, col):
                    possible_wumpus_locs.append(AgentState(row, col, UP))

                if self.kb.is_maybe_safe(row, col):
                    no_pit = Inference((row, col))
                    no_pit.has_pit = False
                    pit = Inference((row, col))
                    pit.has_pit = True
                    maybe_unsafe_locs.append(no_pit)
                    maybe_unsafe_locs.append(pit)

        if self.plan:
            # check that next step in plan is still safe
            state = AgentState(self.position[0], self.position[1], self.kb.get_direction())
            state = state.go(self.plan[0], test=True)
            if state in unsafe_locs:
                self.plan = [] # throw out plan

        # if treasure here, grab and plan shortest route to exit
        if percept[2] == "Glitter":
            self.action = "Grab"
            route = self.make_plan([self.start], safe_locs)
            self.plan.extend(route)
            self.plan.append("Climb")
            self.goal = "Exit"
            return self.action

        # if no treasure, plan shortest route to safe location
        if not self.plan and not self.goal == "Exit":
            self.plan = self.make_plan(unvisited_safe_locs, safe_locs)

        # if there is no safe route, guess where wumpus is and shoot
        if not self.plan and self.kb.has_arrow() and not self.goal == "Exit":
            plan = self.plan_shot(possible_wumpus_locs, safe_locs)
            if plan is not None:
                plan.append("Shoot")
                self.plan = plan

        # if there is no plan, take a risk
        if not self.plan and maybe_unsafe_locs and not self.goal == "Exit":
            probs = self.get_risk_probabilities(maybe_unsafe_locs)

            if probs:
                # get location with the highest probability of not having a pit
                safest = max(probs, key=probs.get)

                for direction in directions:
                    goal = AgentState(safest.x_pos, safest.y_pos, direction)
                    safe_locs.append(goal)
                self.plan = self.make_plan([goal], safe_locs)

        # if there is still no plan, climb out of cave
        if not self.plan:
            plan = self.make_plan([self.start], safe_locs)
            plan.append("Climb")
            self.plan = plan

        self.action = self.plan.pop(0)
        return self.action

    def is_possible(self, world, query):
        # checks that query square doesn't have pit in this world
        if world[world.index(query)].has_pit:
            return False

        for square in world:
            adjacent_squares = self.get_adjacent_pairs(square)
            for pair in adjacent_squares:
                if self.all_false(pair, world):
                    return False
        return True

    def get_adjacent_pairs(self, square):
        up_square = (square.x_pos - 1, square.y_pos + 1)
        down_square = (square.x_pos + 1, square.y_pos - 1)
        squares = []

        if is_valid(up_square[0], up_square[1]):
            squares.append((Inference(up_square), square))

        if is_valid(down_square[0], down_square[1]):
            squares.append((Inference(down_square), square))

        return squares

    def all_false(self, queries, world):
        for loc in queries:
            if loc in world:
                square = world[world.index(loc)]
            else:
                return False
            if square.has_pit:
                return False
        return True

    def get_risk_probabilities(self, frontier):
        probs = {} # stores probability of no pit for each square in frontier

        for square in frontier:

            # only compute probability for no pit
            if square.has_pit:
                continue

            probs[square] = []
            pit_combs = combinations(frontier, len(set(frontier)))

            for world in pit_combs:
                unique_combo = set(world) # removes combinations with repeated squares
                prob = 1
                if len(unique_combo) == len(world) and self.is_possible(world, square):
                    for loc in world:
                        if loc != square: # remove query square from consideration
                            if loc.has_pit:
                                prob = prob * PIT_PRIOR
                            else:
                                prob = prob * (1 - PIT_PRIOR)
                    probs[square].append(prob)

            probs[square] = sum(probs[square]) * (1 - PIT_PRIOR)

        return probs

    def get_valid_actions(self, location):
        actions = ["TurnLeft", "TurnRight", "Forward"]

        for direction in directions:
            if direction == location.direction:
                if not self.direction_valid(location, direction):
                    actions.remove("Forward")

        return actions

    def direction_valid(self, location, direction):
        loc = location.go(direction, test=True)
        if loc:
            return True
        return False

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

            for direction in directions:
                pos = wumpus.go(direction, test=True)
                if pos:
                    pos.reverse()
                    shooting_locs.append(pos)

        return self.make_plan(shooting_locs, world, exact=True)

    def is_allowed(self, state, world, exact):
        if exact:
            if state in world:
                return True
        else:
            for loc in world:
                if state.get_location() == loc.get_location():
                    return True
        return False

    def is_goal(self, state, goal, exact):
        if exact:
            if state == goal:
                return True
        else:
            if state.get_location() == goal.get_location():
                return True
        return False

    def make_plan(self, dest, world, exact=False):
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

                if self.is_goal(state, goal, exact):
                    return explored[state]

                actions = self.get_valid_actions(state)

                # loops through all squares connected to shortest square
                for action in actions:
                    frontier_path = explored[state] + [action]
                    frontier_cost = len(frontier_path)
                    result = self.take_action(state, action)

                    # if this square hasn't been explored yet or we encountered a shorter path to this explored square
                    if self.is_allowed(result, world, exact) and (result not in explored.keys() or frontier_cost < len(explored[result])):
                        path_cost = self.get_distance(result, goal) + frontier_cost
                        result.cost = path_cost
                        frontier.put(result)  # places shortest on frontier
                        explored[result] = frontier_path  # marks location as explored

                        # if this location leads to goal and path to get there is shorter than current solution
                        if self.is_goal(result, goal, exact) and frontier_cost < cost:
                            path = frontier_path
                            cost = frontier_cost

            paths.append((path, cost))

        if paths:
            return min(paths, key = lambda t: t[1])[0]
        return None
