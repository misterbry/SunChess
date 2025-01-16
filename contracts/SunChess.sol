// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract SunChess is ERC721Enumerable, ERC721URIStorage, Ownable {
	using Strings for uint256;
	event Request(string indexed name, address indexed addr);
	event Reward(string indexed name, string indexed achievement, uint256 indexed reward);

	IERC20 public snac;
	uint256 public tokenId;
	uint256 public playerId;
	uint256 public botId;
	uint256 public gameId;
	uint256 public pot;
	string public message;
	mapping(uint256 => string) private _tokenURIs;
	mapping(address => Game) public game;
	mapping(address => Player) public player;
	mapping(string => address) private _names;
	Game[] public games;
	Player[] public players;
	Bot[] public bots;
	Player[] private _requests;

	struct Player {
		string username;
		address payable addr;
		uint256 id;
		string record;
		uint256 elo;
		bool isContributor;
		uint256 level;
	}

	struct Bot {
		string name;
		uint256 id;
		string record;
		uint256 elo;
	}

	struct Game {
		uint256 id;
		string moves;
		string player;
		string bot;
	}

	constructor(string memory name, string memory symbol, address snacAddress) ERC721(name, symbol) Ownable(msg.sender) {
		snac = IERC20(snacAddress);
		tokenId = 0;
		playerId = 0;
		botId = 0;
		gameId = 0;
		message = "Welcome to SunChess! Control this message by becoming a chess master.";
	}
	
	// override conflicting functions
	
	function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721Enumerable, ERC721URIStorage) returns (bool) {
		return super.supportsInterface(interfaceId);
	}

	function _increaseBalance(address account, uint128 value) internal virtual override(ERC721, ERC721Enumerable) {
		super._increaseBalance(account, value);
	}

	function _update(address to, uint256 tokenId_, address auth) internal virtual override(ERC721, ERC721Enumerable) returns (address) {
		return super._update(to, tokenId_, auth);
	}

	function tokenURI(uint256 tokenId_) public view virtual override(ERC721, ERC721URIStorage) returns (string memory) {
		return super.tokenURI(tokenId_);
	}

	function mint(address to_, string memory uri) public payable {
		_safeMint(to_, tokenId);
		_setTokenURI(tokenId, uri);
		tokenId++;
	}

	function _msgValue() internal view virtual returns (uint256) {
		return msg.value;
	}

	function requestPlayer(string memory name, address playerAddr) public {
		require(_names[name] == address(0), "That name is already taken.");
		Player memory request = Player({username: name, addr: payable(playerAddr), id: 0, record: "0/0/0", elo: 1200, isContributor: false, level: 0});
		_requests.push(request);
		emit Request(name, playerAddr);
	}

	function getRequests() public view onlyOwner returns (Player[] memory) {
		return _requests;
	}
	
	function approvePlayer(uint256 index, bool approval) public onlyOwner {
		if (approval) {
			playerId++;
			Player memory newPlayer = _requests[index];
			require(_names[newPlayer.username] == address(0), "That name is already taken.");
			newPlayer.id = playerId;
			players.push(newPlayer);
			player[newPlayer.addr] = newPlayer;
			_names[newPlayer.username] = newPlayer.addr;
			_requests[index] = _requests[_requests.length -1];
			_requests.pop();
			mint(newPlayer.addr, "https://my/very/cool/uri");
		}
		else {
			_requests[index] = _requests[_requests.length -1];
			_requests.pop();			
		}
	}

	function getPlayer(address addr) public view returns (Player memory) {
		return player[addr];
	}

	function getPlayers() public view returns (Player[] memory) {
		return players;
	}

	function depositSnacs(uint256 amt) public {
		snac.transfer(address(this), amt);
	}

	function rewardSnacs(address to, uint256 amt) public onlyOwner {
		snac.transfer(to, amt);
	}

	/* function newBot(string memory botName, uint256 eloRating) public onlyOwner { */
	/* 	Bot memory bot = Bot({ name: botName, id: botId, record: "", elo: eloRating }); */
	/* 	bots.push(bot); */
	/* } */

	function createGame() public {
		Player memory user = player[msg.sender];
		Game memory newGame = Game({id: gameId, moves: "", player: user.username, bot: bots[user.level].name});
		games.push(newGame);
		game[msg.sender] = newGame;
	}

	function saveGame(string memory moveString) public {
		Game memory gameToSave = game[msg.sender];
		gameToSave.moves = moveString;
		game[msg.sender] = gameToSave;
	}

	function loadGame() public view returns (Game memory) {
		return game[msg.sender];
	}

	function gameWin() public {
		Player memory winner = player[msg.sender];
		// require(player.addr == msg.sender, "User and player mismatch, reverting.");
		winner.level += 1;
		player[msg.sender] = winner;
	}

	function createBot(string memory botName, uint256 botElo) public onlyOwner {
		Bot memory newBot = Bot({ name: botName, id: botId, record: "", elo: botElo });
		bots.push(newBot);
	}
}
