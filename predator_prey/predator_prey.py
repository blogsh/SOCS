from __future__ import division
import numpy as np
import numpy.random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from noise import snoise2
import random


PREDATOR = "Predator"
PREY = "Prey"

class Agent:
    def __init__(self, type, pos):
        self.type = type
        self.pos = pos
        self.time_since_last_meal = 0

class PredatorPreyModel:
    initial_predator_count = 100
    initial_prey_count = 200
    starvation_time = 100
    prey_birth_probability = 0.06
    predator_birth_rate = 0.5
    movement_rate = 0.8
    grid_shape = (100, 100)

    def __init__(self, period = 30, water_level=0.2):
        width, height = self.grid_shape
        self.terrain = self.generate_terrain(water_level=water_level, period=period, 
                                             fractal_depth=2, randomly=True)
        self.lattice = [[[] for _ in range(width)] for _ in range(height)]
        self.agents = []
        [self.create_agent(PREDATOR) for i in range(self.initial_predator_count)]
        [self.create_agent(PREY)     for i in range(self.initial_prey_count)]

    def run(self, animating = False, iteration_count = 10000):
        
        population_counts = np.zeros((2, iteration_count), dtype=int)
        
        def loop(t):
            self.step()
            for agent in self.agents:
                if agent.type == PREDATOR:
                    population_counts[0,t] += 1
                else:
                    population_counts[1,t] += 1
            if np.any(population_counts[:,t] == 0):
                return population_counts[:,:t+1]
            if animating:
                self.draw()
        
        if animating:
            figure = plt.figure()
            animation = FuncAnimation(figure, loop, init_func=self.init_drawing,
                                      frames=iteration_count)
        else:
            for t in range(iteration_count):
                loop(t)
            animation = None
            
        return population_counts, animation
    
    def init_drawing(self):
        # NOTE(Pontus): This rescales the colormap so that zero is in the middle
        # terrain_max = np.amax(abs(self.terrain))
        # plt.imshow(self.terrain.T, cmap=plt.cm.coolwarm,
        #            vmin = -terrain_max, vmax = terrain_max)
        plt.imshow(self.terrain.T < 0, cmap=plt.cm.gray, vmin=-3, vmax=1, interpolation="nearest")
        plt.axis("tight")
        plt.gca().get_xaxis().set_visible(False)
        plt.gca().get_yaxis().set_visible(False)
        
        self.predator_plot, = plt.plot([], [], "r.")
        self.prey_plot,     = plt.plot([], [], "g.")
    
    
    def draw(self):
        predator_positions = np.array([agent.pos for agent in self.agents
                                                 if agent.type == PREDATOR])
        prey_positions = np.array([agent.pos for agent in self.agents
                                                 if agent.type == PREY])
        self.predator_plot.set_data(predator_positions.T)
        self.prey_plot.set_data(prey_positions.T)
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
            
        agent = Agent(type, pos)
        x, y = pos
        self.lattice[x][y].append(agent)
        self.agents.append(agent)
        return agent
        
    def remove_agent(self, agent):
        x, y = agent.pos
        self.lattice[x][y].remove(agent)
        self.agents.remove(agent)
    
    def step(self):
        for agent in self.agents:
            agent.time_since_last_meal += 1
            # die
            if agent.time_since_last_meal > self.starvation_time:
                self.remove_agent(agent)
                continue
            
            # move
            # TODO(Pontus): Maybe just remove the movement rate and let the
            # current position be a possible new position?
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
                if self.is_safe_position(agent.pos):
                    agent.time_since_last_meal = 0
                # Reproduce
                if random.random() < self.prey_birth_probability:
                    self.create_agent(PREY, near=prey.pos)
            
            if agent.type == PREDATOR:
                predator = agent
                # Eat and reproduce
                for (x, y) in self.neighbors(predator.pos):
                    for neighbor in self.lattice[x][y]:
                        if neighbor.type == PREY:
                            predator.time_since_last_meal = 0
                            self.remove_agent(neighbor)
                            if random.random() < self.predator_birth_rate:
                                self.create_agent(PREDATOR, near=predator.pos)
            
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
    period = 10
    water_level = 0.1
    world = PredatorPreyModel(period, water_level)
    counts, animation = world.run(animating = True, iteration_count = 100)
    if animation:
        animation.save("PredPreyAnimation.mp4", fps=30, codec="libx264")
        plt.show()
    
    fig, ((map_plot, dynamics_plot), (phase_plot, frequency_plot)) = plt.subplots(2, 2)

    map_plot.imshow(world.terrain.T < 0, cmap=plt.cm.gray, vmin=-3, vmax=1)
    map_plot.set_title("Period: {}".format(period))
    
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
    f = np.fft.rfftfreq(counts.shape[1])[1:]
    
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