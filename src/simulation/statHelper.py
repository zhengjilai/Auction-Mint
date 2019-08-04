import numpy as np
from scipy.stats import geom, norm
import math


'''
sample from geometric distribution
@:param e the expectation of geometric distribution 
@:param N the number of data point to be sampled and calculate average
'''
def sample_from_geometric_distribution(e, N):

    # geometry distribution parameter
    p = 1.0 / e

    while True:

        # sample N bids from geometric distribution
        r = geom.rvs(p, size=N)

        # calculate the average of all N sampled data point
        feedback = math.floor(r.mean())

        # ensure that feedback is positive, or sample feedback again
        if feedback > 0:
           break

    return feedback


'''
sample from norm distribution
@:param loc the expectation of norm distribution
@:param scale the scale of norm distribution
'''
def sample_from_norm_distribution(loc, scale):

    return norm.rvs(loc=loc, scale=scale, size=1)[0]


# the main function to test
if __name__ == '__main__':

    print(sample_from_geometric_distribution(1000000, 10))
    print(sample_from_norm_distribution(0, 1))
