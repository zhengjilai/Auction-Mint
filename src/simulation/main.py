from src.simulation.simulation import Simulation

if __name__ == '__main__':

    # the main function for auction simulation

    # initial parameters
    # initial total balance of the system
    totalBalance = 2400000000000

    # the block reward for a single round
    blockReward = 0.00004 * totalBalance

    # the expected mining expense for a single bidder
    miningExpense = 0.000006 * totalBalance

    # the transaction fees of the first round
    transactionFees = 0.00005 * totalBalance

    # the number of bid winners
    bidWinner = 10

    # if simulation needs to be traced
    traceTag = True

    # the simulation object
    simulation = Simulation(totalBalance, blockReward, miningExpense, bidWinner, transactionFees, traceTag)

    # simulate round by round
    totalRound = 350000
    for i in range(totalRound):
        simulation.single_round()

    simulation.draw_time_series()


