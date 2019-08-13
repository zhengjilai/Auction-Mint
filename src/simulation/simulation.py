import numpy as np
from .statHelper import *
from .draw import *
import math

# class for aucMint simulation
class Simulation:

    def __init__(self, tb, br, me, bw, tf, tt=True, cprop=False, rprop=False, pt=0, gamma=0.5, ur=1/15000):

        # system total balance
        self.totalBalance = tb

        # block reward for a single round (for bid winners altogether)
        self.blockReward = br
        self.blockRewardRate = br / tb

        # average mining expense for a single miner
        self.miningExpense = me
        self.miningExpenseRate = me / tb

        # the number of bid winners
        self.bidWinner = bw

        # the transaction fee predicted from total balance,
        self.transactionFeePredict = tf

        # the fluctuating exchange coefficient
        self.exchangeCoefficient = tf / tb
        # the update rate of exchange coefficient
        self.updateRate = ur
        # the exchange coefficient constant
        # Here we assume that the target exchangeCoefficient = exCoeffConstant * pow(totalBalance, gamma),
        # where exCoeffConstant is a constant throughout the simulation
        self.gamma = gamma
        self.exCoeffConstant = self.exchangeCoefficient / math.pow(self.totalBalance, self.gamma)

        # simulation round
        # initialized as 1
        self.round = 1

        # if simulation needs to be traced
        self.traceTag = tt
        # True if use C-prop, False to use C-const
        self.update_mining_cost_tag = cprop
        # True if use R-prop, False to use R-const
        self.update_block_reward_tag = rprop

        # the perturbation type
        self.perturbation_type = pt

        # simulation result
        # [round, totalBalance, bidPrice. txFee]
        self.result = np.array([
            [0, self.totalBalance, 0, self.transactionFeePredict]
        ])

    def single_round(self):

        # the bid price of this round
        bid_price = self.__calculate_bid()

        # information for this round
        round_info = np.array([[self.round, self.totalBalance, bid_price, self.transactionFeePredict]])

        # data tracing
        if self.traceTag:
            self.trace_result(bid_price)

        # concatenate self.result with info of this round
        self.result = np.concatenate((self.result, round_info), axis=0)

        # update totalBalance, blockReward, miningCost and exchangeCoefficient for the next round, optional
        self.__update_total_balance(bid_price)
        if self.update_block_reward_tag:
            self.__update_block_reward_from_total_balance()
        if self.update_mining_cost_tag:
            self.__update_mining_cost_from_total_balance()
        self.__update_exchange_coefficient_from_total_balance()
        
        # update transaction fee for the next round
        self.transactionFeePredict = self.__update_predict_transaction_fee_from_total_balance()

        # make perturbations
        self.__make_perturbations(self.perturbation_type)

        # update round number
        self.round += 1

    def __calculate_bid(self):

        # time of sampling
        sample_times = self.bidWinner * 20

        # sample mining cost from geometric distribution
        mining_cost = sample_from_geometric_distribution(self.miningExpense, sample_times)

        # the expected yield rate of bidders
        yield_rate = 1.05

        # bid price for a single bidder
        return ((self.blockReward + self.transactionFeePredict) / self.bidWinner - mining_cost) / yield_rate

    def __update_total_balance(self, bid_price):

        # in each round, total balance will increase the amount of block reward (minted)
        self.totalBalance += self.blockReward

        # in each round, token for bid will burnt
        self.totalBalance -= (self.bidWinner * bid_price)

    def __update_predict_transaction_fee_from_total_balance(self):

        # calc the predicted tx fee for the next round
        # calculate the expected tx fee from total balance, with Exchange equation of exchange
        expected_fee = self.totalBalance * self.exchangeCoefficient

        # sample from nor distribution
        return sample_from_norm_distribution(expected_fee, expected_fee / 40)
    
    def __update_block_reward_from_total_balance(self):

        # calc the block reward for the next round
        self.blockReward = self.blockRewardRate * self.totalBalance

    def __update_mining_cost_from_total_balance(self):

        # calc the mining cost for the next round
        self.miningExpense = self.miningExpenseRate * self.totalBalance

    def __update_exchange_coefficient_from_total_balance(self):

        # calc the exchange coefficient for the next round
        # gradually update exchangeCoefficient to the expected ex coefficient
        self.exchangeCoefficient += (self.exCoeffConstant * math.pow(self.totalBalance, self.gamma)
                                   - self.exchangeCoefficient) * self.updateRate

    def __make_perturbations(self, perturbation_type):

        # perturbation type decides which kind of perturbation will be deployed
        # 1 indicates instant increase/decrease in total supply
        # 2 indicates instant increase/decrease in exchange coefficient
        # else indicates doing nothing
        if perturbation_type == 1:
            if self.round == 150000:
                self.totalBalance *= 0.975
            elif self.round == 300000:
                self.totalBalance *= 1.025

        elif perturbation_type == 2:
            if self.round == 150000:
                self.exchangeCoefficient *= 1.025
            elif self.round == 300000:
                self.exchangeCoefficient *= 0.975
        else:
            pass

    def trace_result(self, bid_price):

        if self.round % 1000 == 0:
            print("====================================")
            print("Simulation Round: ", self.round)
            print("Total balance: ", self.totalBalance, self.totalBalance / self.totalBalance)
            print("Tx Fee: ", self.transactionFeePredict, self.transactionFeePredict / self.totalBalance)
            print("Mining cost: ", self.miningExpense, self.miningExpense / self.totalBalance)
            print("Block Reward: ", self.blockReward, self.blockReward / self.totalBalance)
            print("Bid Price: ", bid_price, bid_price / self.totalBalance)
            print("Exchange Coefficient: ", self.exchangeCoefficient)
            print("====================================")

    def draw_time_series(self):

        draw_all(self.result)
