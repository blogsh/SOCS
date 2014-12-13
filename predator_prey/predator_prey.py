import numpy as np
import numpy.random
import matplotlib.pyplot as plt
from scipy.misc import imread

PREDATOR = "Predator"
PREY = "Prey"

class Agent:
    pass

class ElevationWorld:
    initial_predator_count = 10
    initial_prey_count = 20
    predator_death_probability = 0.2
    prey_birth_probability = 0.3
    movement_rate = 0.5
    preferred_elevation = {PREDATOR: 0.1, PREY: 0.9}

    def __init__(self, map_file = "patchy_map.png"):
        self.map_file = map_file
        self.elevation = imread(self.map_file, flatten = True)
        self.size = self.elevation.shape[0]
        self.lattice = [[[] for _ in range(self.size)] for _ in range(self.size)]
        self.agents = []
        [self.create_agent(PREDATOR) for i in range(self.initial_predator_count)]
        [self.create_agent(PREY)     for i in range(self.initial_prey_count)]

    def run(self, animation = False, iteration_count = 10000):
        counts = np.zeros((2, iteration_count), dtype=int)
        for t in range(iteration_count):
            self.step()
            if animation:
                self.draw()
            for agent in self.agents:
                if agent.type == PREDATOR:
                    counts[0,t] += 1
                else:
                    counts[1,t] += 1
        return counts
            
    def create_agent(self, type):
        pos = np.random.randint(self.size, size=2)
        # The more crowded, the less new agents
        if not self.is_empty_position(pos):
            return None
            
        agent = Agent()
        agent.x, agent.y = pos
        agent.type = type
        agent.preferred_elevation = self.preferred_elevation[type]
        
        self.lattice[agent.x][agent.y].append(agent)
        self.agents.append(agent)
        return agent
        
    def remove_agent(self, agent):
        self.lattice[agent.x][agent.y].remove(agent)
        self.agents.remove(agent)
    
    def step(self):
        for agent in self.agents:
            # move
            if np.random.rand() < self.movement_rate:
                # prefer directions that lead closer to preferred elevation
                new_positions = list(filter(self.is_empty_position,
                                            self.neighbors((agent.x, agent.y))))
                if not new_positions:
                    continue
                weights = [1 / abs(self.elevation[new_pos] - agent.preferred_elevation)
                           for new_pos in new_positions]
                probabilities = np.array(weights) / np.sum(weights)
                i = np.random.choice(len(new_positions), p=probabilities)
                new_x, new_y = new_positions[i]
                self.lattice[agent.x][agent.y].remove(agent)
                self.lattice[new_x][new_y].append(agent)
                agent.x, agent.y = new_x, new_y
            
            if agent.type == PREY:
                prey = agent
                # reproduce
                if np.random.rand() < self.prey_birth_probability:
                    self.create_agent(PREY)
            
            if agent.type == PREDATOR:
                predator = agent
                # eat and reproduce
                for (x, y) in self.neighbors((predator.x, predator.y)):
                    for neighbor in self.lattice[x][y]:
                        if neighbor.type == PREY:
                            self.remove_agent(neighbor)
                            self.create_agent(PREDATOR)
                            # Could use for local births
                            # neighbor.type = PREDATOR 
                        
                # die from old age
                if np.random.rand() < self.predator_death_probability:
                    self.remove_agent(predator)
            
    def neighbors(self, pos):
        x, y = pos
        directions = ((1,0), (-1,0), (0,1), (0,-1))
        return filter(self.is_in_bounds, 
                      ( (x + dx, y + dy) for (dx, dy) in directions ))

    def is_empty_position(self, pos):
        x, y = pos
        occupied = self.lattice[x][y]
        return not occupied and self.is_in_bounds(pos)
    
    def is_in_bounds(self, pos):
        x, y = pos
        return (0 <= x < self.size) and (0 <= y < self.size)
        
        
    def draw(self):
        plt.imshow(self.elevation)
        size = (len(self.agents), 2)
        predator_positions = np.zeros(size, dtype = int)
        prey_positions     = np.zeros(size, dtype = int)
        for i, agent in enumerate(self.agents):
            if agent.type == PREDATOR:
                predator_positions[i, :] = agent.x, agent.y
            else:
                prey_positions[i, :]     = agent.x, agent.y
        plt.plot(predator_positions[:,0], predator_positions[:, 1], "ro")
        plt.plot(prey_positions[:,0], prey_positions[:, 1], "go")
        plt.axis("tight")
        plt.draw()
        plt.pause(0.00001)
        plt.cla()


if __name__ == '__main__':
    for map_index, map_file in enumerate(["maps/empty.png", "maps/blocky.png"]):
        iteration_count = 1000
        world = ElevationWorld(map_file)
        counts = world.run(animation = False, iteration_count=iteration_count)
        
        # Plots over time
        # TODO(Pontus): These plots should have the same limits
        plt.subplot(2, 2, map_index + 1)
        plt.title(map_file)
        plt.plot(counts[0,:])
        plt.plot(counts[1,:])
        plt.legend([PREDATOR, PREY])
        
        # Plots over frequency
        plt.subplot(2, 2, 2 + map_index + 1)
        import numpy.fft
        # NOTE(Pontus): Skip constant freq f = 0
        counts_fft = abs(np.fft.rfft(counts))[:,1:] 
        f = np.fft.rfftfreq(iteration_count)[1:]
        plt.plot(f, counts_fft[0,:])
        plt.plot(f, counts_fft[1,:])
        plt.legend([PREDATOR, PREY])
        plt.axis("tight")
    plt.show()