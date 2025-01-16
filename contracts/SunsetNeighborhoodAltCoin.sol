// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract SunsetNeighborhoodAltCoin is ERC20 {
	constructor() ERC20("SunsetNeighborhoodAltCoin", "SNAC") {
		_mint(msg.sender, 26000);
	}
}
