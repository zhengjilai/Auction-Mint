import matplotlib.pyplot as plt
import numpy as np

'''
draw all time series graph
@:param result the result calculated from simulation
'''
def drawAll(result):
    rounds = result[:, 0]
    totalBalance = result[:, 1]
    drawTimeSeries(rounds, totalBalance)

    bidPrice = result[:, 2]
    drawTimeSeries(rounds, bidPrice)

    transactionFee = result[:, 3]
    drawTimeSeries(rounds, transactionFee)

def drawTimeSeries(xaxis, yaxis):
    plt.plot(xaxis, yaxis)
    plt.show()


