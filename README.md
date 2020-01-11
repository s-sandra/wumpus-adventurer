# Wumpus Adventurer
This graphical Wumpus World simulator, created by Stephen Davies and based on implementations from 
[aimacode]( https://github.com/aimacode/aima-python), displays the actions of an `ExplorerAgent` object as it navigates through a 
fictional grid world. [Wumpus World]( https://www.javatpoint.com/the-wumpus-world-in-artificial-intelligence) is a quintessential 
AI toy problem, where an adventurer is tasked with finding gold in a partially-observable cave environment, all while avoiding 
bottomless pits, walls and a deadly beast called the wumpus. For each play, the simulator randomly generates a new 4 x 4 world. 
Using Stephen’s existing framework, I inherited from the `ExplorerAgent` base class as `ashtabna_ExplorerAgent`, which contains 
algorithms for representing knowledge and carrying out inferences, allowing the agent to make rational decisions.

## Percepts
The adventurer can perceive only the following five things as it ventures through the cave. In all cases, it cannot determine what 
direction the percept came from.

- <b>Breeze</b> If the AI feels a breeze, then it is in a location adjacent to one or more pits.
- <b>Stench</b> This means that there must be a wumpus in one of the adjacent rooms.
- <b>Glitter</b> If the AI sees a glitter, then there must be treasure in one of the adjacent rooms.
- <b>Scream</b> If the AI hears a scream, then it knows that the wumpus has died. This can only occur if the adventurer shoots an 
arrow in the wumpus’ direction.
- <b>Bump</b> If this happens, then the AI hit an obstacle.

## Actions
The agent can do the following.

- <b>Climb</b> This only makes sense if the agent is at its initial position and wants to climb out of the cave.
- <b>Shoot</b> This is only applicable if the adventurer has an arrow. The AI begins the game with only one arrow.
- <b>Grab</b> If the agent is in the same room as the treasure, they can grab it. Otherwise, this action is pointless.
- <b>Forward</b> The agent can go forward in its current direction. This will only fail if there is a wall in the way.
- <b>TurnLeft/TurnRight</b> This allows the agent to change orientation.

## Performance Measure
As the simulation progresses, the agent’s overall performance is listed at the bottom of the simulator screen in blue. To maximize reward, 
the agent must successfully grab treasure, return to its starting location and climb out of the cave. However, there are environments 
in which it is impossible to obtain treasure (e.g., the gold is surrounded by pits), so the agent must be intelligent enough to 
give up and leave emptyhanded. 

- <b>+1000</b> If the agent climbs out of the cave with gold.
- <b>-1</b> For each action the agent takes (except shooting an arrow).
- <b>-10</b> For shooting an arrow.
- <b>-1000</b> If the agent falls down a pit or gets eaten by the wumpus.

## Strategy
My agent approaches the problem by treating goals according to their priority. It uses A* search to attempt to create plans by 
querying its knowledge base. After each action, it updates its knowledge base to make more accurate inferences about the world. 
If the agent does not perceive any treasure, then it plans a route to the nearest unvisited safe location. In the event that 
it has exhausted all of its safe options, the agent attempts to open up a route by shooting the wumpus. As a last resort, 
it takes a risk, selecting the room with the highest likelihood of being safe. If all else fails, the agent plans the shortest 
path to the exit and gives up.

## Interface
The wumpus world simulator requires the name of the `ExplorerAgent` class (`ashtabna_ExplorerAgent` in this case) as the first command line 
argument. You can also pass it the following arguments.

- <b>Interactive Mode</b> Allows you to run one step of the AI at a time by pressing the “Go” button. To do this, pass the `interactive` 
argument.
- <b>Auto Mode</b> To run the AI automatically rather than manually, pass the `auto` argument.
- <b>Run Multiple Simulations</b> To run many games, pass the `suite=<number>` argument. This will output descriptive statistics for 
all the requested simulations, rather than display the graphical simulator.
- <b>Specify Random Seed</b> To generate the same wumpus world for each play, pass the seed number as the last argument.

### Presets
The simulator has several available presets. Note that some features are remnants of an older assignment and do not have any 
functionality.

- <b>Iterations</b> Has no function.
- <b>Continuous</b> If this field is checked, the simulator runs the AI continuously and you will be able to see its actions without 
having to press the “Go” button. Can also pass the `auto` argument in the command line.
- <b>Delay</b> If the continuous field is checked and the simulator is in interactive mode, then you can set the delay between AI iterations to make the automation slower or 
faster.

