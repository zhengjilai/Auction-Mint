import numpy as np
from scipy.stats import geom
import math

'''
sample from geometric distribution
@:param e the expectation of geometric distribution 
@:param N the number of data point to be sampled and calculate average
'''
def sample_from_geometric_distribution(e, N):

    # geometry distribution parameter
    p = 1.0 / e

    # sample N bids from geometric distribution
    r = geom.rvs(p, size = N)

    # calculate the average of all N sampled data point
    feedback = math.floor(r.mean())
    print(feedback)
    return feedback



sample_from_geometric_distribution(1000000, 10)