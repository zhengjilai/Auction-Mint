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
    perturbation_type = 1

    # True if use C-prop, False to use C-const
    update_mining_cost_tag = False
    # True if use R-prop, False to use R-const
    update_block_reward_tag = False
    # the simulation object
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

    labels = ["R-const, C-const", "R-const, C-prop", "R-prop, C-const", "R-prop, C-prop"]
    draw_multiple(simulation_propC_propR.result[:, 0],
                  [simulation_constC_constR.result[:, 1], simulation_propC_constR.result[:, 1],
                   simulation_constC_propR.result[:, 1], simulation_propC_propR.result[:, 1]],
                  labels , "Round Number", "Total Supply")


if __name__ == '__main__':
    # perturbation_simulation()
    ablation_simulation()
