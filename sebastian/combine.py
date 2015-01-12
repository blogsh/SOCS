import pickle
import numpy as np

with open('output55.dat') as f:
	data1 = pickle.load(f)

with open('output55.2.dat') as f:
	data2 = pickle.load(f)

growth_rate = []
death_rate = []
nsum = []

for i in range(len(data1)):
	dataset = data1[i]

	gr = dataset['growth_rate']
	dr = dataset['death_rate']

	ds = filter(lambda d: d['growth_rate'] == gr, data2)
	ds = filter(lambda d: d['death_rate'] == dr, ds)

	data1[i]['nsum'] += ds[0]['nsum']

with open('output_combined.dat', 'w+') as f:
	pickle.dump(data1, f)
