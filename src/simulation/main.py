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

    # the number of bid winners
    bidWinner = 10

    # the simulation object
    simulation = Simulation(totalBalance, blockReward, miningExpense, bidWinner)

    # simulate round by round
    totalRound = 350000
    for i in range(totalRound):
        simulation.single_round()
        if i % 1000 == 0:
            print(i)
        if i == 100000:
            simulation.totalBalance *= 0.95
        if i == 200000:
            simulation.totalBalance *= 1.05


    simulation.draw_time_series()


