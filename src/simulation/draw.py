import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker

'''
draw all time series graph
@:param result the result calculated from simulation
'''
def draw_all(result):

    rounds = result[:, 0]
    total_balance = result[:, 1]
    draw_plain(axis_x=rounds, axis_y=total_balance, label_x="Round Number", label_y="Total Supply")

    bid_price = result[:, 2]
    draw_average_as_light(axis_x=rounds, axis_y=bid_price, label_x="Round Number", label_y="Bid Price")

    transaction_fee = result[:, 3]
    draw_average_as_light(axis_x=rounds, axis_y=transaction_fee, label_x="Round Number", label_y="Transaction Fees")


'''
draw time series of color pink from axis_x and axis_y
with an additional average line of color firebrick 
'''
def draw_average_as_light(axis_x, axis_y, label_x="label_x", label_y="label_y"):

    fig, ax = plt.subplots(1)

    # draw the original data
    ax.plot(axis_x[1:], axis_y[1:], color="pink")

    # the round number to calculate average
    average_round = 400
    # calculate average for original data
    aver_axis_y = np.array([sum(axis_y[i-average_round//2:i+average_round//2])/average_round
                 for i in range(average_round//2, len(axis_y)-average_round//2)])

    # draw the averaged data
    ax.plot(axis_x[average_round//2: len(axis_y)-average_round//2], aver_axis_y, color="firebrick")
    ax.set_xlabel(label_x)
    ax.set_ylabel(label_y)
    formatter = mticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-1, 1))
    ax.yaxis.set_major_formatter(formatter)
    formatter2 = mticker.ScalarFormatter(useMathText=True)
    formatter2.set_scientific(True)
    formatter2.set_powerlimits((-1, 1))
    ax.xaxis.set_major_formatter(formatter2)
    plt.show()


'''
draw time series of color firebrick from axis_x and axis_y
'''
def draw_plain(axis_x, axis_y, label_x="label_x", label_y="label_y"):

    # draw the original data
    fig, ax = plt.subplots(1)

    ax.plot(axis_x, axis_y, color="firebrick")
    ax.set_xlabel(label_x)
    ax.set_ylabel(label_y)

    formatter = mticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-1, 1))
    ax.yaxis.set_major_formatter(formatter)
    formatter2 = mticker.ScalarFormatter(useMathText=True)
    formatter2.set_scientific(True)
    formatter2.set_powerlimits((-1, 1))
    ax.xaxis.set_major_formatter(formatter2)
    plt.show()


'''
draw multiple lines with the same axis_x
'''
def draw_multiple(axis_x, axis_y, labels, colors, line_styles, label_x="label_x", label_y="label_y"):

    if len(axis_y) != len(colors) or len(axis_y) != len(labels) or len(axis_y) != len(line_styles):
        return

    # draw the original data
    fig, ax = plt.subplots(1)

    for i in range(len(axis_y)):
        ax.plot(axis_x, axis_y[i], color=colors[i], linestyle=line_styles[i], label=labels[i])

    ax.set_xlabel(label_x)
    ax.set_ylabel(label_y)

    formatter = mticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-1, 1))
    ax.yaxis.set_major_formatter(formatter)
    formatter2 = mticker.ScalarFormatter(useMathText=True)
    formatter2.set_scientific(True)
    formatter2.set_powerlimits((-1, 1))
    ax.xaxis.set_major_formatter(formatter2)
    plt.legend(loc='best', labelspacing=0)
    plt.show()