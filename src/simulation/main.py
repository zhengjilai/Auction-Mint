from src.simulation.simulation import Simulation
from src.simulation.draw import *

def perturbation_simulation():

    # the main function for perturbation simulation

    # initial parameters
    # initial total balance of the system
    total_balance = 1000000000000

    # the block reward for a single round
    block_reward = 0.000035 * total_balance

    # the expected mining expense for a single bidder
    mining_expense = 0.000006 * total_balance

    # the transaction fees of the first round
    transaction_fees = 0.00006 * total_balance

    # the number of bid winners
    bid_winner = 10

    # if simulation needs to be traced in console
    trace_tag = True
    # True if use C-prop, False to use C-const
    update_mining_cost_tag = False
    # True if use R-prop, False to use R-const
    update_block_reward_tag = False

    # perturbation type decides which kind of perturbation will be deployed
    # 1 indicates instant increase/decrease in total supply
    # 2 indicates instant increase/decrease in fisher coefficient
    # else for doing nothing
    perturbation_type = 1

    # the simulation object
    simulation = Simulation(total_balance, block_reward, mining_expense, bid_winner,
                            transaction_fees, trace_tag, update_mining_cost_tag,
                            update_block_reward_tag, perturbation_type)

    # simulate round by round
    total_round = 500000
    for i in range(total_round):
        simulation.single_round()

    simulation.draw_time_series()

def ablation_simulation():

    # the main function for ablation simulation

    # initial parameters
    # initial total balance of the system
    total_balance = 1000000000000

    # the block reward for a single round
    block_reward = 0.000035 * total_balance

    # the expected mining expense for a single bidder
    mining_expense = 0.000006 * total_balance

    # the transaction fees of the first round
    transaction_fees = 0.00006 * total_balance

    # the number of bid winners
    bid_winner = 10

    # if simulation needs to be traced in console
    trace_tag = True

    # perturbation type decides which kind of perturbation will be deployed
    # 1 indicates instant increase/decrease in total supply
    # 2 indicates instant increase/decrease in fisher coefficient
    # else for doing nothing
    perturbation_type = 0

    # True if use C-prop, False to use C-const
    update_mining_cost_tag = False
    # True if use R-prop, False to use R-const
    update_block_reward_tag = False

    # the simulation objects
    simulation_constC_constR = Simulation(total_balance, block_reward, mining_expense, bid_winner,
                            transaction_fees, trace_tag, update_mining_cost_tag,
                            update_block_reward_tag, perturbation_type)

    update_mining_cost_tag = True
    update_block_reward_tag = False
    simulation_propC_constR = Simulation(total_balance, block_reward, mining_expense, bid_winner,
                            transaction_fees, trace_tag, update_mining_cost_tag,
                            update_block_reward_tag, perturbation_type)

    update_mining_cost_tag = False
    update_block_reward_tag = True
    simulation_constC_propR = Simulation(total_balance, block_reward, mining_expense, bid_winner,
                            transaction_fees, trace_tag, update_mining_cost_tag,
                            update_block_reward_tag, perturbation_type)

    update_mining_cost_tag = True
    update_block_reward_tag = True
    simulation_propC_propR = Simulation(total_balance, block_reward, mining_expense, bid_winner,
                            transaction_fees, trace_tag, update_mining_cost_tag,
                            update_block_reward_tag, perturbation_type)

    # simulate round by round
    total_round = 100000
    for i in range(total_round):
        simulation_constC_constR.single_round()
        simulation_constC_propR.single_round()
        simulation_propC_constR.single_round()
        simulation_propC_propR.single_round()

    # legend labels
    labels = ["R-const, C-const", "R-const, C-prop", "R-prop, C-const", "R-prop, C-prop"]
    # colors and line styles for drawing
    colors = ["firebrick", "goldenrod", "dodgerblue", "forestgreen"]
    line_styles = ["-", "-", "-", "-"]
    draw_multiple(simulation_propC_propR.result[:, 0],
                  [simulation_constC_constR.result[:, 1], simulation_propC_constR.result[:, 1],
                   simulation_constC_propR.result[:, 1], simulation_propC_propR.result[:, 1]],
                  labels, colors, line_styles, "Round Number", "Total Supply")


def sensitivity_simulation_for_kxe0():
    # the main function for sensitivity simulation for kxe0

    # initial parameters
    # initial total balance of the system
    total_balance = 1000000000000

    # the block reward for a single round
    block_reward = 0.000035 * total_balance

    # the expected mining expense for a single bidder
    mining_expense = 0.000006 * total_balance

    # the number of bid winners
    bid_winner = 10

    # if simulation needs to be traced in console
    trace_tag = True

    # perturbation type decides which kind of perturbation will be deployed
    # 1 indicates instant increase/decrease in total supply
    # 2 indicates instant increase/decrease in fisher coefficient
    # else for doing nothing
    perturbation_type = 0

    # True if use C-prop, False to use C-const
    update_mining_cost_tag = False
    # True if use R-prop, False to use R-const
    update_block_reward_tag = False

    # the transaction fees of the first round
    transaction_fees = [0.00004 * total_balance, 0.00005 * total_balance,
                        0.00006 * total_balance, 0.00007 * total_balance, 0.00008 * total_balance]

    # construct simulation objects with different transaction fees
    simulations = []
    for i in range(len(transaction_fees)):
        simulations.append(Simulation(total_balance, block_reward, mining_expense, bid_winner,
                            transaction_fees[i], trace_tag, update_mining_cost_tag,
                            update_block_reward_tag, perturbation_type))

    # total round number
    round_number = 100000
    # simulation process
    for j in range(round_number):
        for i in range(len(transaction_fees)):
            simulations[i].single_round()

    # legend labels
    labels = [r"$k^{ex}_{0} = 4 \times 10^{-5}$", r"$k^{ex}_{0} = 5 \times 10^{-5}$",
              r"$k^{ex}_{0} = 6 \times 10^{-5}$", r"$k^{ex}_{0} = 7 \times 10^{-5}$", r"$k^{ex}_{0} = 8 \times 10^{-5}$"]
    # colors and line styles for drawing
    colors = ['#FFB5C5', "#FF3030", "#EE2C2C", "#CD2626", "#8B1A1A"]
    line_styles = ["-", "-", "-", "-", "-"]
    simulation_results = [simulations[i].result[:, 1] for i in range(len(transaction_fees))]
    draw_multiple(simulations[0].result[:, 0],
                  simulation_results,
                  labels, colors, line_styles, "Round Number", "Total Supply")


def sensitivity_simulation_for_gamma():
    # the main function for sensitivity simulation for gamma

    # initial parameters
    # initial total balance of the system
    total_balance = 1000000000000

    # the block reward for a single round
    block_reward = 0.000035 * total_balance

    # the expected mining expense for a single bidder
    mining_expense = 0.000006 * total_balance

    # the transaction fees of the first round
    transaction_fees = 0.00006 * total_balance

    # the number of bid winners
    bid_winner = 10

    # if simulation needs to be traced in console
    trace_tag = True

    # perturbation type decides which kind of perturbation will be deployed
    # 1 indicates instant increase/decrease in total supply
    # 2 indicates instant increase/decrease in fisher coefficient
    # else for doing nothing
    perturbation_type = 0

    # True if use C-prop, False to use C-const
    update_mining_cost_tag = False
    # True if use R-prop, False to use R-const
    update_block_reward_tag = False

    # the gammas
    gammas = [0.25, 0.5, 0.75, 1, 2]

    # construct simulation objects with different gammas
    simulations = []
    for i in range(len(gammas)):
        simulations.append(Simulation(total_balance, block_reward, mining_expense, bid_winner,
                            transaction_fees, trace_tag, update_mining_cost_tag,
                            update_block_reward_tag, perturbation_type, gammas[i]))

    # total round number
    round_number = 150000
    # simulation process
    for j in range(round_number):
        for i in range(len(gammas)):
            simulations[i].single_round()

    # legend labels
    labels = [r"$\gamma = 0.25$", r"$\gamma = 0.5$",
              r"$\gamma = 0.75$", r"$\gamma = 1$", r"$\gamma = 2$"]
    # colors and line styles for drawing
    colors = ['#FFB5C5', "#FF3030", "#EE2C2C", "#CD2626", "#8B1A1A"]
    line_styles = ["-", "-", "-", "-", "-"]
    simulation_results = [simulations[i].result[:, 1] for i in range(len(gammas))]
    draw_multiple(simulations[0].result[:, 0],
                  simulation_results,
                  labels, colors, line_styles, "Round Number", "Total Supply")


def sensitivity_simulation_for_update_rate():
    # the main function for sensitivity simulation for gamma

    # initial parameters
    # initial total balance of the system
    total_balance = 1000000000000

    # the block reward for a single round
    block_reward = 0.000035 * total_balance

    # the expected mining expense for a single bidder
    mining_expense = 0.000006 * total_balance

    # the transaction fees of the first round
    transaction_fees = 0.00006 * total_balance

    # the number of bid winners
    bid_winner = 10

    # if simulation needs to be traced in console
    trace_tag = True

    # perturbation type decides which kind of perturbation will be deployed
    # 1 indicates instant increase/decrease in total supply
    # 2 indicates instant increase/decrease in fisher coefficient
    # else for doing nothing
    perturbation_type = 0

    # True if use C-prop, False to use C-const
    update_mining_cost_tag = False
    # True if use R-prop, False to use R-const
    update_block_reward_tag = False

    # the gamma
    gamma = 0.5

    # the update rates for exchange coefficient
    update_rates = [1/100, 1/1000, 1/5000, 1/15000, 1/50000]

    # construct simulation objects with different transaction fees
    simulations = []
    for i in range(len(update_rates)):
        simulations.append(Simulation(total_balance, block_reward, mining_expense, bid_winner,
                            transaction_fees, trace_tag, update_mining_cost_tag,
                            update_block_reward_tag, perturbation_type, gamma, update_rates[i]))

    # total round number
    round_number = 150000
    # simulation process
    for j in range(round_number):
        for i in range(len(update_rates)):
            simulations[i].single_round()

    # legend labels
    labels = [r"$ur = 1/100$", r"$ur = 1/1000$",
              r"$ur = 1/5000$", r"$ur = 1/15000$", r"$ur = 1/50000$"]
    # colors and line styles for drawing
    colors = ['#FFB5C5', "#FF3030", "#EE2C2C", "#CD2626", "#8B1A1A"]
    line_styles = ["-", "-", "-", "-", "-"]
    simulation_results = [simulations[i].result[:, 1] for i in range(len(update_rates))]
    draw_multiple(simulations[0].result[:, 0],
                  simulation_results,
                  labels, colors, line_styles, "Round Number", "Total Supply")


if __name__ == '__main__':
    # perturbation_simulation()
    # ablation_simulation()
    # sensitivity_simulation_for_kxe0()
    # sensitivity_simulation_for_gamma()
    sensitivity_simulation_for_update_rate()
