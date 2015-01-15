from __future__ import division
import numpy as np
import numpy.random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from noise import snoise2
import random
from datetime import datetime
import os
import multiprocessing as mp
import itertools
from matplotlib.mlab import griddata

PREDATOR = "Predator"
PREY = "Prey"

class Agent:
    def __init__(self, type, pos):
        self.type = type
        self.pos = pos
        self.time_since_last_meal = 0

class PredatorPreyModel:
    initial_prey_count = 200
    starvation_time = 50
    prey_birth_probability = 0.06
    predator_birth_rate = 0.1
    movement_rate = 0.8
    grid_shape = (100, 100)

    def __init__(self, initial_predator_count = 10, water_level = 0.2):
        self.initial_predator_count = initial_predator_count
        width, height = self.grid_shape
        self.terrain = self.generate_terrain(water_level=water_level, period=30, 
                                             fractal_depth=2, randomly=True)
        self.lattice = [[[] for _ in range(width)] for _ in range(height)]
        self.agents = []
        [self.create_agent(PREDATOR) for i in range(self.initial_predator_count)]
        [self.create_agent(PREY)     for i in range(self.initial_prey_count)]

    def run(self, animating = False, iteration_count = 10000):
        
        population_counts = np.zeros((2, iteration_count), dtype=int)
        
        def loop(t):
            if animating:
                self.draw()
            self.step()
            for agent in self.agents:
                if agent.type == PREDATOR:
                    population_counts[0,t] += 1
                else:
                    population_counts[1,t] += 1
        
        if animating:
            figure = plt.figure()
            figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
            animation = FuncAnimation(figure, loop, init_func=self.init_drawing,
                                      frames=iteration_count)
            # save video
            directory = "videos"
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename = "{}/{}.mp4".format(directory, datetime.now())
            animation.save(filename, fps=20, codec="libx264", extra_args=['-pix_fmt','yuv420p'])
        else:
            animation = None
            for t in range(iteration_count):
                loop(t)
                if np.any(population_counts[:,t] == 0):
                    return population_counts[:, :t + 1]
        
        return population_counts
    
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
        if predator_positions.size:
            self.predator_plot.set_data(predator_positions.T)
        else:
            self.predator_plot.set_data([],[])
            
        if prey_positions.size:
            self.prey_plot.set_data(prey_positions.T)
        else:
            self.prey_plot.set_data([],[])
        plt.draw()
        plt.pause(0.0001)
    
    def generate_terrain(self, period, water_level = 0, fractal_depth = 2, randomly=False):
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

def plot_landscape(model, water_level):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    width, height = model.grid_shape
    x, y = np.meshgrid(range(width), range(height))
    terrain = model.generate_terrain(period=50)
    ax.plot_surface(x, y, terrain, rstride=5, cstride=5, cmap=plt.cm.coolwarm)
    
    fig, ax = plt.subplots()
    ax.imshow(model.terrain.T < 0, cmap=plt.cm.gray, vmin=-3, vmax=1)

def plot_analysis(model, population_counts):
    fig, ((map_plot, dynamics_plot), (phase_plot, frequency_plot)) = plt.subplots(2, 2)
    
    map_plot.imshow(model.terrain.T < 0, cmap=plt.cm.gray, vmin=-3, vmax=1)
    
    dynamics_plot.plot(population_counts.T)
    dynamics_plot.legend([PREDATOR, PREY])
    dynamics_plot.set_title("Population dynamics")
    dynamics_plot.set_xlabel(r"Time $t$")
    dynamics_plot.set_ylabel(r"Population size")
    
    phase_plot.plot(population_counts[0,:], population_counts[1,:])
    phase_plot.set_title("Phase diagram")
    phase_plot.set_xlabel("Predator")
    phase_plot.set_ylabel("Prey")
    
    import numpy.fft
    # NOTE(Pontus): Skip constant freq f = 0
    population_counts_fft = abs(np.fft.rfft(population_counts))[:,1:] 
    f = np.fft.rfftfreq(population_counts.shape[1])[1:]
    
    frequency_plot.plot(f, population_counts_fft[0,:], label=PREDATOR)
    frequency_plot.plot(f, population_counts_fft[1,:], label=PREY)
    frequency_plot.legend()
    frequency_plot.set_title("Frequency domain")
    frequency_plot.set_xlabel("Frequency")
    frequency_plot.set_ylabel("Amplitude")
    frequency_plot.set_xscale("log")
    frequency_plot.set_yscale("log")
    frequency_plot.axis("tight")

#@np.vectorize
def extinction_plot(pred0, water_level, sample_count = 10, iteration_count=10000):
    print("pred0:", pred0, "water_level:", water_level)
    sum = 0
    for run in range(sample_count):
        initial_predator_count = int(pred0 / (1 - pred0) * PredatorPreyModel.initial_prey_count)
        model = PredatorPreyModel(initial_predator_count, water_level)
        population_counts = model.run(animating=False, iteration_count=iteration_count)
        final_time = population_counts.shape[1]
        extinction = (final_time != iteration_count)
        if extinction:
            sum += final_time
    average = sum / sample_count
    print(average)
    return pred0, water_level, average
    
def plot_average_extinction_time(sample_count = 10, iteration_count = 10000):
    pred0s = np.linspace(0.01, 0.5, 5)
    water_levels = np.linspace(-1, 0.4, 5)
    #pred0s, water_levels = np.meshgrid(pred0s, water_levels)
    #extinction_time = extinction_plot(pred0s, water_levels)

    pool = mp.Pool(8)
    tasks = [pool.apply_async(extinction_plot, args=args) for args in itertools.product(pred0s, water_levels)]
    pred0s, water_levels, extinction_time = zip(*[t.get() for t in tasks])

    xi = np.linspace(min(pred0s), max(pred0s))
    yi = np.linspace(min(water_levels), max(water_levels))

    X, Y = np.meshgrid(xi, yi)
    Z = griddata(pred0s, water_levels, extinction_time, xi, yi)

    directory = "data"
    if not os.path.exists(directory):
        os.makedirs(directory)
    np.savetxt(directory + "/pred0s.tsv", X)
    np.savetxt(directory + "/water_levels.tsv", Y)
    np.savetxt(directory + "/extinction_time.tsv", Z)
    plt.figure()
    contours = plt.contour(X, Y, Z)
    plt.clabel(contours, inline=1)
    plt.xlabel(r"Initial fraction of predators")
    plt.ylabel(r"Water level")
    plt.colorbar()

if __name__ == '__main__':
    
    # model = PredatorPreyModel(initial_predator_count=100, water_level = -1)
    # population_counts = model.run(animating=True, iteration_count=10000)
    # plot_analysis(model, population_counts)
    plot_average_extinction_time(sample_count = 10)
    
    plt.show()