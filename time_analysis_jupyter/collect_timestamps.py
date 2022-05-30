

import pickle
import numpy as np
import matplotlib.pyplot as plt

times = []
with open("times.pkl", 'rb') as f:
    total = 0
    try:
        while True:
            new_times = pickle.load(f)
            times.extend(new_times)
            total += 1
    except:
        print(total)


times = np.array(times)

np.diff(times)


