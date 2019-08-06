import numpy as np
from .statHelper import *
from .draw import *
import math

# class for aucMint simulation
class Simulation:

    def __init__(self, tb, br, me, bw, tf, tt=True, pt=0):

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

        '''
        # the fluctuating exchange coefficient and the base exchange coefficient
        self.exchangeCoefficient = tf / tb
        self.exchangeCoefficientAtFirst = self.exchangeCoefficient
        '''

        # the fluctuating exchange coefficient
        self.exchangeCoefficient = tf / tb
        # the exchange coefficient update rate
        # Here we assume that the expected exchangeCoeff = updateRate * sqrt(totalBalance),
        # where updateRate is a constant
        self.exchangeCoefficientUpdateRate = self.exchangeCoefficient / math.sqrt(tb)

        # the number of former rounds used to predict the next round transaction fee
        self.predictRoundNumber = 100

        # simulation round
        # initialized as 1
        self.round = 1

        # if simulation needs to be traced
        self.traceTag = tt

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
        # self.__update_block_reward_from_total_balance()
        # self.__update_mining_cost_from_total_balance()
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

    '''
    # deprecated
    def __update_predict_transaction_fee_with_former_fee(self):

        # calc the predicted tx fee for the next round
        # before self.predictRoundNumber, minus txfee in round 0
        if self.round <= self.predictRoundNumber:
            feeMidCalc = (self.transactionFeePredict * self.predictRoundNumber
                          - self.result[0][3] + self.result[self.round][3]) / self.predictRoundNumber
        # after that, minus txfee in round self.round - self.predictRoundNumber
        else:
            feeMidCalc = (self.transactionFeePredict * self.predictRoundNumber
                          - self.result[self.round - self.predictRoundNumber][3]
                          + self.result[self.round][3]) / self.predictRoundNumber

        # modify the prediction with Exchange equation of exchange
        return feeMidCalc / self.result[self.round][1] * self.totalBalance
    '''

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

    '''
    def __update_exchange_coefficient_from_total_balance(self):

        # calc the exchange coefficient for the next round
        update_rate = 1/15000
        self.exchangeCoefficient += (self.exchangeCoefficientAtFirst / self.result[0][1] * self.totalBalance
                                   - self.exchangeCoefficient) * update_rate
    '''

    def __update_exchange_coefficient_from_total_balance(self):

        # calc the exchange coefficient for the next round
        update_rate = 1/15000
        # gradually update exchangeCoefficient to the expected one
        self.exchangeCoefficient += (self.exchangeCoefficientUpdateRate * math.sqrt(self.totalBalance)
                                   - self.exchangeCoefficient) * update_rate

    def __make_perturbations(self, perturbation_type):

        # perturbation type decides which kind of perturbation will be deployed
        # 1 indicates instant increase/decrease in total supply
        # 2 indicates instant increase/decrease in exchange coefficient
        # else indicates doing nothing
        if perturbation_type == 1:
            if self.round == 125000:
                self.totalBalance *= 0.975
            elif self.round == 250000:
                self.totalBalance *= 1.025

        elif perturbation_type == 2:
            if self.round == 125000:
                self.exchangeCoefficient *= 1.025
            elif self.round == 250000:
                self.exchangeCoefficient /= 1.025
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
