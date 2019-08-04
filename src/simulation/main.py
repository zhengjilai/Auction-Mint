from src.simulation.simulation import Simulation

if __name__ == '__main__':

    # the main function for auction simulation

    # initial parameters
    # initial total balance of the system
    totalBalance = 1800000000000

    # the block reward for a single round
    blockReward = 0.00004 * totalBalance

    # the expected mining expense for a single bidder
    miningExpense = 0.000006 * totalBalance

    # the transaction fees of the first round
    transactionFees = 0.00005 * totalBalance

    # the number of bid winners
    bidWinner = 10

    # the simulation object
    simulation = Simulation(totalBalance, blockReward, miningExpense, bidWinner, transactionFees)

    # simulate round by round
    totalRound = 350000
    for i in range(totalRound):
        simulation.single_round()

        # show simulation round
        if i % 1000 == 0:
            print(i)

    simulation.draw_time_series()


