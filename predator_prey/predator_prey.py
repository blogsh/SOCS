from __future__ import division
import numpy as np
import numpy.random
import matplotlib.pyplot as plt
from noise import snoise2
import random

PREDATOR = "Predator"
PREY = "Prey"

class Agent:
    pass

class PredatorPreyModel:
    initial_predator_count = 200
    initial_prey_count = 200
    predator_death_probability = 0.02
    prey_birth_probability = 0.06
    predator_birth_rate = 0.8
    movement_rate = 1
    grid_shape = (100, 100)

    def __init__(self):
        width, height = self.grid_shape
        self.terrain = self.generate_terrain(water_level=0.2, period=50, 
                                             fractal_depth=2, randomly=True)
        self.lattice = [[[] for _ in range(width)] for _ in range(height)]
        self.agents = []
        [self.create_agent(PREDATOR) for i in range(self.initial_predator_count)]
        [self.create_agent(PREY)     for i in range(self.initial_prey_count)]

    def run(self, animating = False, iteration_count = 10000):
        population_counts = np.zeros((2, iteration_count), dtype=int)
        if animating:
            # NOTE(Pontus): This rescales the colormap so that zero is in the middle
            terrain_max = np.amax(abs(self.terrain))
            plt.imshow(self.terrain.T, cmap=plt.cm.coolwarm, 
                       vmin = -terrain_max, vmax = terrain_max)
            predator_line, = plt.plot([], [], "ro")
            prey_line,     = plt.plot([], [], "go")
            self.predator_plot = predator_line
            self.prey_plot     = prey_line
            
        for t in range(iteration_count):
            self.step()
            if animating:
                self.draw()
            for agent in self.agents:
                if agent.type == PREDATOR:
                    population_counts[0,t] += 1
                else:
                    population_counts[1,t] += 1
        plt.close()
        return population_counts
    
        
        
    def draw(self):
        # TODO(Pontus): These should not be allocated at each timestep
        size = (len(self.agents), 2)
        predator_positions = np.zeros(size, dtype = int)
        prey_positions     = np.zeros(size, dtype = int)
        for i, agent in enumerate(self.agents):
            if agent.type == PREDATOR:
                predator_positions[i, :] = agent.pos
            else:
                prey_positions[i, :]     = agent.pos
        self.predator_plot.set_data(predator_positions[:,0], predator_positions[:, 1])
        self.prey_plot.set_data(prey_positions[:,0], prey_positions[:, 1])
        plt.draw()
        plt.pause(0.0001)
    
    def generate_terrain(self, water_level, period, fractal_depth, randomly=False):
        """
        Generates a pseudo-random terrain matrix. 
        Values > 0 are land and values < 0 are water.
        `water_level` is a number between -1 and 1, where -1 is all land and 1 is all ocean.
        `period` controls the shape of the landscape.
        If `randomly` is false, the same landscape will be generated every time.
        """
        if randomly:
            start = random.random() * 1e5
        else:
            start = 0
        width, height = self.grid_shape
        terrain_iterator = (snoise2(start + i / period, start + j / period, fractal_depth) 
                            for i in range(width)
                            for j in range(height))
        return np.fromiter(terrain_iterator, float).reshape(self.grid_shape) - water_level
    
    def create_agent(self, type, near=None):
        if near:
            pos = random.choice(list(self.neighbors(near)))
        else:
            pos = tuple(random.randrange(size) for size in self.grid_shape)
            
        # NOTE(Pontus): This makes sure that
        # the more crowded it is, the less agents will be born
        if not self.is_safe_position(pos):
            return None
            
        agent = Agent()
        agent.type = type
        agent.pos = x, y = pos
        self.lattice[x][y].append(agent)
        self.agents.append(agent)
        return agent
        
    def remove_agent(self, agent):
        x, y = agent.pos
        self.lattice[x][y].remove(agent)
        self.agents.remove(agent)
    
    def step(self):
        for agent in self.agents:
            # move
            if random.random() < self.movement_rate:
                new_positions = list(filter(self.is_empty_position,
                                            self.neighbors(agent.pos)))
                if not new_positions:
                    continue
                new_x, new_y = random.choice(new_positions)
                self.lattice[new_x][new_y].append(agent)
                x, y = agent.pos
                self.lattice[x][y].remove(agent)
                agent.pos = new_x, new_y
            
            if agent.type == PREY:
                prey = agent
                # Reproduce
                if random.random() < self.prey_birth_probability:
                    self.create_agent(PREY, near=prey.pos)
            
            if agent.type == PREDATOR:
                predator = agent
                # Eat and reproduce
                for (x, y) in self.neighbors(predator.pos):
                    for neighbor in self.lattice[x][y]:
                        if neighbor.type == PREY:
                            if random.random() < self.predator_birth_rate:
                                neighbor.type = PREDATOR 
                                # NOTE(Pontus): They are vampires ;)
                            else:
                                self.remove_agent(neighbor)
                        
                # Die
                if random.random() < self.predator_death_probability:
                    self.remove_agent(predator)
            
    def neighbors(self, pos):
        x, y = pos
        directions = ((1,0), (-1,0), (0,1), (0,-1))
        return filter(self.is_in_bounds, 
                      ( (x + dx, y + dy) for (dx, dy) in directions ))
    
    def is_safe_position(self, pos):
        is_on_land = (self.terrain[pos] > 0)
        return is_on_land and self.is_empty_position(pos)
    
    def is_empty_position(self, pos):
        x, y = pos
        occupied = self.lattice[x][y]
        return not occupied and self.is_in_bounds(pos)
    
    def is_in_bounds(self, pos):
        x, y = pos
        x_max, y_max = self.grid_shape
        return (0 <= x < x_max) and (0 <= y < y_max)
        

if __name__ == '__main__':
    iteration_count = 1000
    world = PredatorPreyModel()
    counts = world.run(animating = False, iteration_count=iteration_count)
    
    fig, (dynamics_plot, phase_plot, frequency_plot) = plt.subplots(1, 3)

    dynamics_plot.plot(counts.T)
    dynamics_plot.legend([PREDATOR, PREY])
    dynamics_plot.set_title("Population dynamics")
    dynamics_plot.set_xlabel(r"Time $t$")
    dynamics_plot.set_ylabel(r"Population size")
    
    phase_plot.plot(counts[0,:], counts[1,:])
    phase_plot.set_title("Phase diagram")
    phase_plot.set_xlabel("Predator")
    phase_plot.set_ylabel("Prey")
    
    import numpy.fft
    # NOTE(Pontus): Skip constant freq f = 0
    counts_fft = abs(np.fft.rfft(counts))[:,1:] 
    f = np.fft.rfftfreq(iteration_count)[1:]
    
    frequency_plot.plot(f, counts_fft[0,:], label=PREDATOR)
    frequency_plot.plot(f, counts_fft[1,:], label=PREY)
    frequency_plot.legend()
    frequency_plot.set_title("Frequency domain")
    frequency_plot.set_xlabel("Frequency")
    frequency_plot.set_ylabel("Amplitude")
    frequency_plot.set_xscale("log")
    frequency_plot.set_yscale("log")
    frequency_plot.axis("tight")
    
    plt.show()