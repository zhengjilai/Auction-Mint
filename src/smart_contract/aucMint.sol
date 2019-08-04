pragma solidity ^0.5.2;

import "./ERC20Modified.sol";

/**
 * @title aucMint.sol
 * @dev except for ERC20, add minting/withdraw Ether logic and blind auction logic
 */

contract aucMint is ERC20Modified{

    // struct for a specific bid
    // used in a map called roundAddressToBid below
    struct Bid {
        // keccak256 result, as a commitment for blind auction
        bytes32 blindedBid;
        // maximum value of this bid, can get back the escrow after the auction ends
        uint escrow;
        // true value of this bid, will be filled after commitment is revealed
        uint trueValue;
        // the tag of whether this bid has been revealed
        bool alreadyRevealed;
        // the tag of whether the commitment is revealed in time
        bool seasonable;
    }

    // struct for a specific blind auction round
    // used in a map called roundInfo below
    struct RoundInfo{
        // the tag of whether this bid round has been liquidated
        bool liquidated;
        // the total transaction fee in this round
        uint transactionFee;
        // the bidding accounts in a specific round
        address[] biddersThisRound;
    }

    // name of token
    string private constant name = "TSY Token";
    // owner of contract, reserved for further privileges
    address private owner;
    // maximum number of winners in each bid round (share the sum of txfee and block reward)
    uint private bidWinnerNumber = 4;
    // block reward for each bid in each bid round
    uint private blockReward = 10000000000000000000;

    /*
    0                               1  com     rev  2  com     rev  3  com    rev   4
    | ============================= | ===== \ ===== | ===== \ ===== | ===== \ ===== | .....
    startTime              blindAuctionTime
    */
    // start time of token: time when token becomes mintable
    uint public startTime;
    // start time of the first blind auction
    uint public blindAuctionTime;
    // duration of a single committing period
    uint public commitDuration;
    // duration of a single revealing period
    uint public revealDuration;

    // the map for finding an account's bid in a specific round
    mapping (address => mapping (uint => Bid)) private roundAddressToBid;
    // the map for finding basic information for a round
    mapping (uint => RoundInfo) private roundInfo;
    // the list of seasonable Addresses in a round, used just for sort in liquidation
    address[] private seasonableAddresses;

    /**
    * @dev Modifier to ensure now is in committing period
    */
    modifier inCommitPeriod {
        // after auction begins
        require(now > blindAuctionTime);
        // in committing period
        require( ((now - blindAuctionTime).mod(commitDuration.add(revealDuration))) < commitDuration);
        _;
    }

    /**
    * @dev Modifier to ensure now is in revealing period
    */
    modifier inRevealPeriod {
        // after auction begins
        require(now > blindAuctionTime);
        // in revealing period
        require( ((now - blindAuctionTime).mod(commitDuration.add(revealDuration))) >= commitDuration);
        _;
    }

    // the event that a commitment is submitted in a committing period
    event BidEvent(address ad, uint escrow);
    // the event that a commitment is revealed
    event RevealEvent(address ad, uint value, bytes32 secret, bool isSeasonableAndValid);

    /**
    * @dev Function to construct some basic parameters
    * @param _mintDuration the duration in which only mint token is available
    * @param _commitDuration the duration in which putting forward commitment is available
    * @param _revealDuration the duration in which revealing commitment is available
    */
    constructor(uint _mintDuration, uint _commitDuration, uint _revealDuration) public{
        require(_mintDuration > 0 && _commitDuration > 0 && _revealDuration > 0);
        startTime = now;
        blindAuctionTime = startTime.add(_mintDuration);
        commitDuration = _commitDuration;
        revealDuration = _revealDuration;
        owner = msg.sender;
    }

    /**
     * @dev Function to determine the exchange rate for Ether and Token
     * @return an exchange rate (uint) of Token : Ether
     */
    function exchangeRate() public view returns (uint){
        // Before blind auction starts, exchange rate is a constant
        if (now <= blindAuctionTime || totalSupply() <= 0) {return 10000;}
        // After blind auction starts, exchange rate fluctuates with totalSupply
        else {return uint(totalSupply().div(address(this).balance));}
    }

    /**
     * @dev Function to determine the round of auction
     * @return the round of auction
     */
    function auctionRound() public view returns (uint){
        if (now < blindAuctionTime) {return 0;}
        else {return uint((now - blindAuctionTime).div(commitDuration.add(revealDuration))).add(1);}
    }

    /**
    * @dev Function to calculate transaction fee
    * @param _value the total amount of token to transfer or mint or burn
    * @return the calculated transaction fee
    */
    function calculateTxFee(uint _value) internal pure returns(uint){
        // receive 1/10000 of _value as transaction fee
        return _value.div(uint(10000));
    }

    /**
     * @dev Function to mint tokens (of msg.value) to msg.sender
     * @return A boolean that indicates if the operation was successful.
     */
    function mint() public payable returns (bool){
        return mintTo(msg.sender);
    }

    /**
     * @dev Function to mint tokens (of msg.value) to an address, having 1/10000 txfee
     * @param _to The address that will receive the minted tokens.
     * @return A boolean that indicates if the operation was successful.
     */
    function mintTo(address _to) public payable returns (bool) {
        uint exRate = exchangeRate();
        if (now > blindAuctionTime && totalSupply() > 0){
            // the original exchangeRate() is smaller, since it does not take msg.value into account
            exRate = exRate.mul(address(this).balance).div(address(this).balance - msg.value);
        }
        // calculate mint value and tx fee
        uint _value = msg.value.mul(exRate);
        uint fee = calculateTxFee(_value);
        // mint _value to the address, while freeze fee as transaction fee
        _mint(_to, _value );
        _freeze(_to , fee);
        // add fee to total transaction fee of this round
        uint aucRound = auctionRound();
        roundInfo[aucRound].transactionFee = roundInfo[aucRound].transactionFee.add(fee);
        return true;
    }

    /**
    * @dev Function to withdraw Ether from Token, with exchange rate of (this).address, having 1/10000 txfee
    * @param _value The value of tsyCoin one wants to withdraw
    * @return A boolean that indicates if the operation was successful.
    */
    function withdrawEther(uint _value) public returns (bool){
        require(_value >= 0 && _value <= balanceOf(msg.sender));
        // calculate transaction fee and remaining token
        uint fee = calculateTxFee(_value);
        uint remaining = _value.sub(fee);
        uint exRate = exchangeRate();
        // burn remaining, while freeze transaction fee
        _burn(msg.sender, remaining);
        _freeze(msg.sender, fee);
        // add fee to total transaction fee of this round
        uint aucRound = auctionRound();
        roundInfo[aucRound].transactionFee = roundInfo[aucRound].transactionFee.add(fee);
        // the actual withdrawing process(only withdraw remaining token)
        msg.sender.transfer(remaining.div(exRate));
        return true;
    }

    /**
     * @dev Transfer token for a specified address, having 1/10000 txfee
     * @param _to The address to transfer to.
     * @param _value The amount to be transferred.
     */
    function transfer(address _to, uint256 _value) public returns (bool) {
        // calculate transaction fee and remaining token
        uint fee = calculateTxFee(_value);
        uint remaining = _value.sub(fee);
        // transfer remaining and freeze fee
        _transfer(msg.sender, _to, remaining);
        _freeze(msg.sender, fee);
        // add fee to total transaction fee of this round
        uint aucRound = auctionRound();
        roundInfo[aucRound].transactionFee = roundInfo[aucRound].transactionFee.add(fee);
        return true;
    }

    /**
    * @dev Function to blind bid for current round's reward and tx fee
    *      Place a blinded bid with `_blindedBid` = keccak256(abi.encodePacked(_value, _secret)).
    *       eg. 0x0000000000000000000000000000000000000000000000000000000000000021
    *      _escrow is the maximum value claimed for this bid, it will be locked before the commitment is opened.
    *      _escrow will be withheld forever if it is less than the committed value
    *      Remember: _value should not exceed _escrow, or token cannot been retrieved from the bid
    * @param _blindedBid the commitment of the bid value(keccak256)
    * @param _escrow the maximum value claimed for this bid
    * @return A boolean that indicates if the operation was successful.
    */
    function bid(bytes32 _blindedBid, uint _escrow) public inCommitPeriod returns(bool)
    {
        // amount of _escrow should not be too little
        require(_escrow > 1000000000);
        uint round = auctionRound();
        // refresh the data of roundInfo and roundAddressToBid
        roundInfo[round].biddersThisRound.push(msg.sender);
        roundAddressToBid[msg.sender][round] = Bid({
                blindedBid: _blindedBid,
                escrow: _escrow,
                trueValue: 0,
                alreadyRevealed: false,
                seasonable: false
            });
        // balance available for msg.sender should be decreased, while total supply does not change
        _freeze(msg.sender, _escrow);
        emit BidEvent(msg.sender, _escrow);
        return true;
    }

    /**
    * @dev Function to reveal commitment for current round's reward and tx fee
    *      reveal _value and secret of the blinded bid where `_blindedBid` = keccak256(abi.encodePacked(_value, _secret)).
    *      if revealing is seasonable: _value will be filled to the Bid struct in roundAddressToBid,
    *                                   while (_escrow - _value) will be sent back to msg.sender
    *      if revealing is not seasonable or not valid: half of escrow will be sent back, the remaining will be burnt as penalty
    *      Liquidation of the bid will be done afterwards
    * @param _round the bid round of the commitment
    * @param _value the bid value corresponding to the commitment
    * @param _secret the secret used to conceal the commitment
    * @return A boolean that indicates if the operation was successful.
    */
    function reveal(uint _round, uint _value, bytes32 _secret) public inRevealPeriod returns(bool){
        // basic check
        require(_round >= 1);
        // the bid to process
        Bid storage bidtoCheck = roundAddressToBid[msg.sender][_round];
        require(bidtoCheck.escrow > 1000000000);
        // It is very important to check whether the commitment has been revealed !!!
        require(bidtoCheck.alreadyRevealed == false);
        // _value should not exceed _escrow
        require(_value <= bidtoCheck.escrow);
        // the current round
        uint roundNow = auctionRound();
        require(roundNow >= _round);

        if (roundNow == _round){ // deployed when revealing is seasonable
            if (bidtoCheck.blindedBid == keccak256(abi.encodePacked(_value,_secret))){
                bidtoCheck.trueValue = _value;
                bidtoCheck.alreadyRevealed = true;
                bidtoCheck.seasonable = true;
                // unfreeze part of token
                _unfreeze(msg.sender, bidtoCheck.escrow - bidtoCheck.trueValue);
                // reveal event
                emit RevealEvent(msg.sender, _value, _secret, true);
            } else{return false;}
        } else{ // deployed when revealing is not seasonable
            if (bidtoCheck.blindedBid == keccak256(abi.encodePacked(_value,_secret))){
                bidtoCheck.trueValue = _value;
                bidtoCheck.alreadyRevealed = true;
                bidtoCheck.seasonable = false;
                // half of escrow will be sent back, the remaining will be burnt
                _unfreeze(msg.sender, bidtoCheck.escrow);
                _burn(msg.sender, bidtoCheck.escrow.div(2));
                // reveal event
                emit RevealEvent(msg.sender, _value, _secret, false);
            }else{return false;}
        }
        return true;
    }

    /**
    * @dev Internal function to liquidate the final bid result in specific round
    * @param round the bid round of the commitment
    * @return A boolean that indicates if the operation was successful.
    */
    function liquidation(uint round) public returns(bool){
        uint currentRound = auctionRound();
        // one can only liquidate previous rounds
        require(currentRound > round);

        // prevent duplicate liquidation
        if (roundInfo[round].liquidated) {return false;}
        // the 0 round(mint only round) of txfee will be sent to the first round bid winners(round 1)
        if (round == 0) {
            roundInfo[round+1].transactionFee = roundInfo[round+1].transactionFee.add(roundInfo[round].transactionFee);
            roundInfo[round].transactionFee = 0;
            roundInfo[round].liquidated = true;
            return true;
        }

        // if the previous round has not been liquidated, recursively process it.
        if (!roundInfo[round - 1].liquidated) {liquidation(round -1);}

        // here we start to liquidate
        // collect the seasonable revealed bid addresses into address[] storage seasonableAddresses
        delete seasonableAddresses;
        for (uint i = 0; i < roundInfo[round].biddersThisRound.length; i++){
            if (roundAddressToBid[ roundInfo[round].biddersThisRound[i] ][round].seasonable){
                seasonableAddresses.push(roundInfo[round].biddersThisRound[i]);
            }
        }

        // case 1: no seasonable bidders in this round
        if (seasonableAddresses.length == 0) {
            // pile up transaction fee if nobody bids
            roundInfo[round+1].transactionFee = roundInfo[round+1].transactionFee.add(roundInfo[round].transactionFee);
            roundInfo[round].transactionFee = 0;
            roundInfo[round].liquidated = true;
            return true;
        }
        // case 2: Number of seasonable Bidders is not enough( <= bidWinnerNumber )
        if (seasonableAddresses.length <= bidWinnerNumber){
            // the minimum bid amount in this round
            uint minimumBid = roundAddressToBid[seasonableAddresses[0]][round].trueValue;
            for (uint i = 0; i < seasonableAddresses.length; i++){
                if (roundAddressToBid[seasonableAddresses[i]][round].trueValue > minimumBid){
                    minimumBid = roundAddressToBid[seasonableAddresses[i]][round].trueValue;
                }
            }
            for (uint i = 0; i < seasonableAddresses.length; i++){
                // every bidder share transactionFee(unfreeze)
                _unfreeze(seasonableAddresses[i], roundInfo[round].transactionFee.div(seasonableAddresses.length));
                // every bidder share blockReward(mint)
                _mint(seasonableAddresses[i], blockReward.div(seasonableAddresses.length));
                // every bidder only pay minimumBid for this bid round(unfreeze and burn)
                _unfreeze(seasonableAddresses[i], roundAddressToBid[seasonableAddresses[i]][round].trueValue);
                _burn(seasonableAddresses[i], minimumBid);
            }
            roundInfo[round].liquidated = true;
            return true;
        }
        // case 3: Number of seasonable Bidders exceeds bidWinnerNumber
        if (seasonableAddresses.length > bidWinnerNumber){
            // sort seasonableAddresses according to its bid value, in descending order
            quickSort(0,seasonableAddresses.length - 1, round);
            // true bid value will be the value of the first bid loser
            uint trueBidValue = roundAddressToBid[seasonableAddresses[bidWinnerNumber]][round].trueValue;
            // the bid winners
            for (uint i = 0; i < bidWinnerNumber; i++){
                // every bidder winner shares transactionFee(unfreeze)
                _unfreeze(seasonableAddresses[i], roundInfo[round].transactionFee.div(bidWinnerNumber));
                // every bidder winner shares blockReward(mint)
                _mint(seasonableAddresses[i], blockReward.div(bidWinnerNumber));
                // every bidder winner only pays trueBidValue for this bid round(unfreeze and burn)
                _unfreeze(seasonableAddresses[i], roundAddressToBid[seasonableAddresses[i]][round].trueValue);
                _burn(seasonableAddresses[i], trueBidValue);
            }
            // the bid losers
            for (uint i = bidWinnerNumber; i < seasonableAddresses.length; i++){
                // bid losers will pay nothing for this bid trial
                _unfreeze(seasonableAddresses[i], roundAddressToBid[seasonableAddresses[i]][round].trueValue);
            }
            return true;
        }
        return false;
    }

    /**
    * @dev Private function to sort seasonableAddresses according to its bid value, in descending order
    *      This function will use quick sort
    * @param left the left index
    * @param right the right index
    * @param round the liquidating round
    */
    function quickSort(uint left, uint right, uint round) private {
        // quick sort boundary conditions
        if (left >= right) {return;}
        uint key = roundAddressToBid[seasonableAddresses[left]][round].trueValue;
        uint i = left;
        uint j = right;
        address temp;
        while (i < j){
            while (i < j && roundAddressToBid[seasonableAddresses[j]][round].trueValue <= key){
                j--;
            }
            while (i < j && roundAddressToBid[seasonableAddresses[i]][round].trueValue >= key){
                i++;
            }
            // swap seasonableAddresses[i] and seasonableAddresses[j]
            temp = seasonableAddresses[i];
            seasonableAddresses[i] = seasonableAddresses[j];
            seasonableAddresses[j] = temp;
        }
        // swap seasonableAddresses[left] and seasonableAddresses[i]
        temp = seasonableAddresses[left];
        seasonableAddresses[left] = seasonableAddresses[i];
        seasonableAddresses[i] = temp;
        // recursively call quickSort
        if (i != 0) {quickSort(left, i-1, round);}
        if (i != seasonableAddresses.length - 1) {quickSort(i+1,right, round);}
        return;
    }

    //  The following are only auxiliary functions only written for test

    /**
    * @dev A test function to calculate `_blindedBid` = keccak256(abi.encodePacked(_value, _secret)).
    * @param _value the bid value corresponding to the commitment
    * @param _secret the secret used to conceal the commitment
    * @return A bytes32 result as the keccak256 result
    */
    function calculateCommitment(uint _value, bytes32 _secret) public pure returns (bytes32){
        bytes32 _blindedBid = keccak256(abi.encodePacked(_value,_secret));
        return _blindedBid;
    }

    /**
    * @dev A test function to query the total transaction fees in a specific round
    * @param round the round number
    * @return the total transaction fee in the specific round
    */
    function queryTransactionFee(uint round) public view returns(uint){
        return roundInfo[round].transactionFee;
    }

    /**
    * @dev A test function to query msg.sender's Bid in a specific round
    * @param round the round number
    * @return the Bid struct content of msg.sender in the specific round
    */
    function queryBid(uint round) public view returns(bytes32, uint, uint, bool, bool){
        return (roundAddressToBid[msg.sender][round].blindedBid,
        roundAddressToBid[msg.sender][round].escrow,
        roundAddressToBid[msg.sender][round].trueValue,
        roundAddressToBid[msg.sender][round].alreadyRevealed,
        roundAddressToBid[msg.sender][round].seasonable);
    }

    /**
    * @dev A test function to query whether now is in Commitment Period
    * @return a bool indicator, true means now is in commitment period, false means the contrary
    */
    function inCommitmentPeriod() public view returns(bool){
        if (now <= blindAuctionTime) return false;
        // in committing period
        if ((now - blindAuctionTime).mod(commitDuration.add(revealDuration)) >= commitDuration) return false;
        return true;
    }
}