import numpy as np
from .statHelper import *
from .draw import *


# class for aucMint simulation
class Simulation:

    def __init__(self, tb, br, me, bw, tf):

        # system total balance
        self.totalBalance = tb

        # block reward
        self.blockReward = br

        # average mining expense for a single miner
        self.miningExpense = me

        # the number of bid winners
        self.bidWinner = bw

        # the transaction fee predicted from total balance,
        self.transactionFeePredict = tf
        # the number of former rounds used to predict the next round transaction fee
        self.predictRoundNumber = 20

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
        self.__update_predict_transaction_fee_from_total_balance()

        # make perturbations
        perturbation_type = 0
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
        self.transactionFeePredict = feeMidCalc / self.result[self.round][1] * self.totalBalance

    def __update_predict_transaction_fee_from_total_balance(self):

        # calc the predicted tx fee for the next round

        # the multiple between total balance and fee, with Fisher Equation
        rate = self.result[0][1] / self.result[0][3]
        # calculate the expected tx fee from total balance
        expectedFee = self.totalBalance / rate
        # sample from nor distribution
        self.transactionFeePredict = sample_from_norm_distribution(expectedFee, expectedFee / 40)

    def __make_perturbations(self, perturbation_type):

        # perturbation type decides which kind of perturbation will be deployed
        # 0 indicates instant increase/decrease in
        if perturbation_type == 0:
            if self.round == 100000:
                self.totalBalance *= 0.975
            if self.round == 200000:
                self.totalBalance *= 1.025
        else:
            pass

    def print_result(self):

        print(self.result)

    def draw_time_series(self):

        drawAll(self.result)