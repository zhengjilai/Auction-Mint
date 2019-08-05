from src.simulation.simulation import Simulation

if __name__ == '__main__':

    # the main function for auction simulation

    # initial parameters
    # initial total balance of the system
    totalBalance = 1000000000000

    # the block reward for a single round
    blockReward = 0.000035 * totalBalance

    # the expected mining expense for a single bidder
    miningExpense = 0.000006 * totalBalance

    # the transaction fees of the first round
    transactionFees = 0.00006 * totalBalance

    # the number of bid winners
    bidWinner = 10

    # if simulation needs to be traced in console
    traceTag = True

    # perturbation type decides which kind of perturbation will be deployed
    # 1 indicates instant increase/decrease in total supply
    # 2 indicates instant increase/decrease in fisher coefficient
    # else for doing nothing
    perturbation_type = 2

    # the simulation object
    simulation = Simulation(totalBalance, blockReward, miningExpense, bidWinner,
                            transactionFees, traceTag, perturbation_type)

    # simulate round by round
    totalRound = 400000
    for i in range(totalRound):
        simulation.single_round()

    simulation.draw_time_series()


