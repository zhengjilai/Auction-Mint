import numpy as np
from .statHelper import *
from .draw import *


# class for aucMint simulation
class Simulation:

    def __init__(self, tb, br, me, bw, tf, tt):

        # system total balance
        self.totalBalance = tb

        # block reward
        self.blockReward = br
        self.blockRewardRate = br / tb

        # average mining expense for a single miner
        self.miningExpense = me
        self.miningExpenseRate = me / tb

        # the number of bid winners
        self.bidWinner = bw

        # the transaction fee predicted from total balance,
        self.transactionFeePredict = tf
        self.fisherCoefficient = tf / tb
        # the number of former rounds used to predict the next round transaction fee
        self.predictRoundNumber = 100

        # simulation round
        # initialized as 1
        self.round = 1

        # if simulation needs to be traced
        self.traceTag = tt

        # simulation result
        # [round, totalBalance, bidPrice. txFee]
        self.result = np.array([
            [0, self.totalBalance, 0, self.transactionFeePredict]
        ])

    def single_round(self):

        # the bid price of this round
        bidPrice = self.__calculate_bid()

        # information for this round
        roundInfo = np.array([[self.round, self.totalBalance, bidPrice, self.transactionFeePredict]])

        # data tracing
        if self.traceTag:
            self.trace_result(bidPrice)

        # concatenate self.result with info of this round
        self.result = np.concatenate((self.result, roundInfo), axis=0)

        # update totalBalance, blockReward and miningCost for the next round
        self.__update_total_balance(bidPrice)
        # self.__update_block_reward_from_total_balance()
        # self.__update_mining_cost_from_total_balance()
        
        # update transaction fee for the next round
        res1 = self.__update_predict_transaction_fee_from_total_balance()
        # res2 = self.__update_predict_transaction_fee_with_former_fee()
        self.transactionFeePredict = res1

        # make perturbations
        perturbation_type = 1
        self.__make_perturbations(perturbation_type)

        # update round number
        self.round += 1

    def __calculate_bid(self):

        # number of sampling
        sampleTimes = self.bidWinner * 20

        # sample mining cost from geometric distribution
        miningCost = sample_from_geometric_distribution(self.miningExpense, sampleTimes)

        # bid price for a single bidder
        return (self.blockReward + self.transactionFeePredict) / self.bidWinner - miningCost

    def __update_total_balance(self, bidPrice):

        # in each round, total balance will increase the amount of block reward (minted)
        self.totalBalance += self.blockReward

        # in each round, token for bid will burnt
        self.totalBalance -= (self.bidWinner * bidPrice)

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

        # modify the prediction with Fisher equation of exchange
        return feeMidCalc / self.result[self.round][1] * self.totalBalance

    def __update_predict_transaction_fee_from_total_balance(self):

        # calc the predicted tx fee for the next round
        # calculate the expected tx fee from total balance, with Fisher equation of exchange
        expectedFee = self.totalBalance * self.fisherCoefficient

        # sample from nor distribution
        return sample_from_norm_distribution(expectedFee, expectedFee / 40)
    
    def __update_block_reward_from_total_balance(self):

        # calc the block reward for the next round
        self.blockReward = self.blockRewardRate * self.totalBalance

    def __update_mining_cost_from_total_balance(self):

        # calc the mining cost for the next round
        self.miningExpense = self.miningExpenseRate * self.totalBalance

    def __make_perturbations(self, perturbation_type):

        # perturbation type decides which kind of perturbation will be deployed
        # 0 indicates instant increase/decrease in
        if perturbation_type == 0:
            if self.round == 100000:
                self.totalBalance *= 0.975
            elif self.round == 200000:
                self.totalBalance *= 1.025
        elif perturbation_type == 1:
            if self.round == 100000:
                self.fisherCoefficient *= 1.05
            elif self.round == 200000:
                self.fisherCoefficient /= 1.05
        else:
            pass

    def trace_result(self, bidPrice):
        if self.round % 1000 == 0:
            print("====================================")
            print("Simulation Round: ", self.round)
            print("Tx Fee: ", self.transactionFeePredict, self.transactionFeePredict / self.totalBalance)
            print("Total balance: ", self.totalBalance, self.totalBalance / self.totalBalance)
            print("Mining cost: ", self.miningExpense, self.miningExpense / self.totalBalance)
            print("Block Reward: ", self.blockReward, self.blockReward / self.totalBalance)
            print("Bid Price: ", bidPrice, bidPrice / self.totalBalance)
            print("====================================")

    def draw_time_series(self):

        drawAll(self.result)
