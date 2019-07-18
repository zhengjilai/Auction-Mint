import numpy as np
from .statHelper import *

# class for aucMint simulation
class Simulation:

    def __init__(self, tb, br, me):

        # system total balance
        self.totalBalance = tb

        # block reward
        self.blockReward = br

        # average mining expense for a single miner
        self.miningExpense = me

        # the number of bid winners
        self.bidWinner = 10

        # the transaction fee predicted from former rounds,
        # initialized as 0.000000001 * totalBalance
        self.transactionFeePredict = 0.000000001 * self.totalBalance
        # the number of former rounds used to predict the next round transaction fee
        self.predictRoundNumber = 1000

        # simulation round
        # initialized as 1
        self.round = 1

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

        # concatenate self.result with info of this round
        self.result = np.concatenate((self.result, roundInfo), axis = 0)

        # update totalBalance and transaction fee for the next round
        self.__update_total_balance(bidPrice)
        self.__update_predict_transaction_fee()

        # update round number
        self.round += 1

    def __calculate_bid(self):

        # number of sampling
        sampleTimes = self.bidWinner * 3

        # sample mining cost from geometric distribution
        miningCost = sample_from_geometric_distribution(self.miningExpense, sampleTimes)

        # bid price for a single bidder
        return (self.blockReward + self.transactionFeePredict) / self.bidWinner - miningCost

    def __update_total_balance(self, bidPrice):

        # in each round, total balance will increase the amount of block reward (minted)
        self.totalBalance += self.blockReward

        # in each round, token for bid will burnt
        self.totalBalance -= (self.bidWinner * bidPrice)

    def __update_predict_transaction_fee(self):

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
        self.transactionFeePredict = feeMidCalc / self.result[self.round][1] * self.totalBalance

    def show_result(self):

        print(self.result)
