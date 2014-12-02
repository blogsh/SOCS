import random
import numpy as np
import numpy.random
from scipy.misc import imread

from environment import World as BaseWorld
from environment import WorldRenderer as BaseWorldRenderer

class Agent:
    pass

class ElevationWorld(BaseWorld):
    SETTINGS =  [
        ("Number of Agents",    "numberOfAgents",       int,    '100'),
        ("Movement Rate",       "movementRate",         float,  '0.5'),
    ]

    def __init__(self, settings):
        BaseWorld.__init__(self, settings)
        self.elevation = imread("testmap.png", flatten = True)
        self.size = self.elevation.shape[0]
        self.lattice = [[[] for _ in range(self.size)] for _ in range(self.size)]
        self.agents = [self.generate_agent() 
                       for i in range(settings['numberOfAgents'])]

    def generate_agent(self):
        agent = Agent()
        while True:
            agent.x = random.randrange(self.size)
            agent.y = random.randrange(self.size)
            if self.is_valid_position((agent.x, agent.y)):
                break
        agent.preferred_elevation = 0.9
        agent.type = random.choice(("Prey", "Predator"))
        self.lattice[agent.x][agent.y].append(agent)
        return agent

    def step(self):
        for agent in self.agents: 
            self.move(agent)

    def move(self, agent):
        if random.random() < self.settings['movementRate']:
            # prefer directions that lead closer to preferred elevation
            directions = ((1,0), (-1,0), (0,1), (0,-1))
            new_positions = filter(self.is_valid_position, 
                        ((agent.x + dx, agent.y + dy) for (dx, dy) in directions))
            weights = [1 / abs(self.elevation[new_pos] - agent.preferred_elevation)
                       for new_pos in new_positions]
            probabilities = np.array(weights) / np.sum(weights)
            i = np.random.choice(len(new_positions), p=probabilities)
            new_x, new_y = new_positions[i]
            self.lattice[agent.x][agent.y].remove(agent)
            self.lattice[new_x][new_y].append(agent)
            agent.x, agent.y = new_x, new_y

    def is_valid_position(self, pos):
        x, y = pos
        out_of_bounds = ((x < 0) or (x >= self.size) or 
                        (y < 0) or (y >= self.size))
        if out_of_bounds:
            return False
        occupied = self.lattice[x][y]
        return not occupied

class ElevationWorldRenderer(BaseWorldRenderer):
    SETTINGS = []

    # No fancy initialization things
    def __init__(self, world, settings):
        BaseWorldRenderer.__init__(self, world, settings)
        self.update_field()

        world.settings.listeners.append(self.on_change_settings)

    def on_change_settings(self, key, value):
        pass

    def update_field(self):
        pass

    def render(self, render):
        render.set_size((self.world.size, self.world.size))
        
        render.background("testmap.png")
        
        # Render the agents with a different color for the two types
        for agent in self.world.agents:
            green = (0.0, 1.0, 0.0)
            blue  = (0.0, 0.0, 1.0)
            color = {"Prey": green, "Predator": blue}[agent.type]
            render.agent((agent.x, agent.y), color)

# If the script is executed as the main script
if __name__ == '__main__':
    from gui import Environment

    env = Environment(ElevationWorld, ElevationWorldRenderer)
    env.run()
