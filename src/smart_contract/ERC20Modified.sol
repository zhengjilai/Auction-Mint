pragma solidity ^0.5.2;

import "./SafeMath.sol";

/**
 * @title Modified ERC20 token
 * remove functions related to '_approve', remove public 'transfer' functions
 * add functions of '_freeze' and '_unfreeze'
 *
 * @dev Implementation of the basic standard token.
 * https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md
 * Originally based on code by FirstBlood:
 * https://github.com/Firstbloodio/token/blob/master/smart_contract/FirstBloodToken.sol
 *
 * This implementation emits additional Approval events, allowing applications to reconstruct the allowance status for
 * all accounts just by listening to said events. Note that this isn't required by the specification, and other
 * compliant implementations may not do it.
 */

contract ERC20Modified{
    using SafeMath for uint256;

    // balance of a specific address
    mapping (address => uint256) private _balances;
    // total supply of token
    uint256 private _totalSupply;

    // event of transfer token from an address to another address
    event Transfer(address from, address to, uint256 value);
    // event of freeze token from an address
    event Freeze(address from, uint256 value);
    // event of unfreeze token to an address
    event UnFreeze(address to, uint256 value);

    /**
     * @dev Total number of tokens in existence
     */
    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    /**
     * @dev Gets the balance of the specified address.
     * @param owner The address to query the balance of.
     * @return An uint256 representing the amount owned by the passed address.
     */
    function balanceOf(address owner) public view returns (uint256) {
        return _balances[owner];
    }

    /**
     * @dev Transfer token for a specified addresses
     * @param from The address to transfer from.
     * @param to The address to transfer to.
     * @param value The amount to be transferred.
     */
    function _transfer(address from, address to, uint256 value) internal {
        require(to != address(0));

        _balances[from] = _balances[from].sub(value);
        _balances[to] = _balances[to].add(value);
        emit Transfer(from, to, value);
    }

    /**
     * @dev Internal function that mints an amount of the token and assigns it to
     * an account. This encapsulates the modification of balances such that the
     * proper events are emitted.
     * @param account The account that will receive the created tokens.
     * @param value The amount that will be created.
     */
    function _mint(address account, uint256 value) internal {
        require(account != address(0));

        _totalSupply = _totalSupply.add(value);
        _balances[account] = _balances[account].add(value);
        emit Transfer(address(0), account, value);
    }

    /**
     * @dev Internal function that burns an amount of the token of a given
     * account.
     * @param account The account whose tokens will be burnt.
     * @param value The amount that will be burnt.
     */
    function _burn(address account, uint256 value) internal {
        require(account != address(0));

        _totalSupply = _totalSupply.sub(value);
        _balances[account] = _balances[account].sub(value);
        emit Transfer(account, address(0), value);
    }

    /**
     * @dev Internal function that freeze an amount of the token and burns it from
     * an account. This is only used for the implementation of auction escrow, since escrow does not
     * increase or decrease the total supply.
     * @param account The account that will burn the frozen tokens.
     * @param value The amount that will be frozen.
     */
    function _freeze(address account, uint256 value) internal {
        require(account != address(0));

        _balances[account] = _balances[account].sub(value);
        emit Freeze(account, value);
    }

    /**
     * @dev Internal function that unfreeze an amount of the token and assigns it t
     * an account. This is only used for the implementation of auction escrow, since escrow does not
     * increase or decrease the total supply.
     * @param account The account that will receive the unfrozen tokens.
     * @param value The amount that will be unfrozen.
     */
    function _unfreeze(address account, uint256 value) internal {
        require(account != address(0));

        _balances[account] = _balances[account].add(value);
        emit UnFreeze(account, value);
    }

}
