import matplotlib.pyplot as plt
import numpy as np

'''
draw all time series graph
@:param result the result calculated from simulation
'''
def drawAll(result):
    rounds = result[:, 0]
    total_balance = result[:, 1]
    drawPlain(axis_x=rounds, axis_y=total_balance, label_x="Round Number", label_y="Total Supply")

    bid_price = result[:, 2]
    drawAverageAsLight(axis_x=rounds, axis_y=bid_price, label_x="Round Number", label_y="Bid Price")

    transaction_fee = result[:, 3]
    drawAverageAsLight(axis_x=rounds, axis_y=transaction_fee, label_x="Round Number", label_y="Transaction Fees")


def drawAverageAsLight(axis_x, axis_y, label_x="label_x", label_y="label_y"):

    # draw the original data
    plt.plot(axis_x, axis_y, color="pink")

    # the round number to calculate average
    average_round = 300
    # calculate average for original data
    aver_axis_y = np.array([sum(axis_y[i-average_round//2:i+average_round//2])/average_round
                 for i in range(average_round//2, len(axis_y)-average_round//2)])

    # draw the averaged data
    plt.plot(axis_x[average_round//2: len(axis_y)-average_round//2], aver_axis_y, color="firebrick")
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.show()


def drawPlain(axis_x, axis_y, label_x="label_x", label_y="label_y"):

    # draw the original data
    plt.plot(axis_x, axis_y, color="firebrick")
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.show()

