// const hre = require("hardhat");
// const { expect } = require("chai");
// const { ethers } = require("hardhat");
import { expect } from "chai";
import pkg from "hardhat";
const hre = pkg;

describe("Testing SunChess contract...", function () {
  let CONTRACT;
  let contract;
  let contractName;
  let SNAC
  let snacContract;
  let snacContractName;
  let owner;
  let bob;
  let alice;
  let addrs;
  let snapshotId;
  const tokenURI = "https://myapi.com/metadata/1";

  before(async () => {
    CONTRACT = await hre.ethers.getContractFactory("SunChess");
    SNAC = await hre.ethers.getContractFactory("SunsetNeighborhoodAltCoin");
    [owner, bob, alice, ...addrs] = await hre.ethers.getSigners();
    snacContract = await SNAC.deploy();
    await snacContract.deployed();
    contract = await CONTRACT.deploy("SunChess", "SUNC", snacContract.address);
    await contract.deployed();
    contractName = await contract.name();
    snacContractName = await snacContract.name();
    console.log("#################################################");
    console.log(snacContractName, "has been deployed to", snacContract.address);
    console.log("#################################################");
    console.log(`Methods for ${contractName} contract: `, ...Object.keys(contract.interface.functions));
    snapshotId = await hre.ethers.provider.send("evm_snapshot", []);
  });

  beforeEach(async function () {
  });

  afterEach(async () => {
    await hre.ethers.provider.send("evm_revert", [snapshotId]);
    snapshotId = await hre.ethers.provider.send("evm_snapshot", []);
  });
  
  // Individual Tests
  
  it("Should deploy the contract and mint a token", async function () {
    await contract.mint(bob.address, tokenURI);
    let ownerBal = await contract.balanceOf(owner.address);
    console.log("Token balance of Owner: ", ownerBal.toString());
    let bobBal = await contract.balanceOf(bob.address);
    console.log("Token balance of Bob: ", bobBal.toString());
    let aliceBal = await contract.balanceOf(alice.address);
    console.log("Token balance of Alice: ", aliceBal.toString());
    expect(await contract.ownerOf(0)).to.equal(bob.address);
    expect(await contract.tokenURI(0)).to.equal(tokenURI);
  });

  it("Should show a lower balance for owner than bob or alice", async function () {
    const ownerBal = await hre.ethers.provider.getBalance(owner.address);
    console.log("Owner: ", ownerBal.toString());
    const bobBal = await hre.ethers.provider.getBalance(bob.address);
    console.log("Bob: ", bobBal.toString());
    const aliceBal = await hre.ethers.provider.getBalance(alice.address);
    console.log("Alice: ", aliceBal.toString());
    expect(ownerBal).to.be < bobBal;
  });

  it("Should allow user to request to be a player", async () => {
    await contract.requestPlayer("Bob", bob.address);
    let requests = await contract.getRequests();
    console.log("REQUESTS: ", requests);
    expect(requests.length).to.equal(1);
    await contract.approvePlayer(0, true);
    let requests2 = await contract.getRequests();
    console.log("AFTER APPROVE REQUESTS: ", requests2);
    expect(requests2.length).to.equal(0);
    try {
      await contract.requestPlayer("Bob", bob.address);
    } catch (error) {
      const decodedData = hre.ethers.utils.defaultAbiCoder.decode(['string'], '0x' + error.data.slice(10));
      console.log(decodedData[0]);
    }
    let player = await contract.getPlayer(owner.address);
    let playerId = await contract.playerId();
    let players = await contract.getPlayers();
  });

  it("Should allow owner to approve one request and deny another.", async () => {
    await contract.requestPlayer("Bob", bob.address);
    await contract.requestPlayer("Alice", alice.address);
    let requests = await contract.getRequests();
    for (const request of requests) {
      console.log("Username: ", request.username);
      console.log("Address: ", request.addr);
    }
    expect(requests.length).to.equal(2);
    await contract.approvePlayer(0, true);
    await contract.approvePlayer(0, true);
    let requests2 = await contract.getRequests();
    expect(requests2.length).to.equal(0);
    let playerId = await contract.playerId();
    expect(playerId.toNumber()).to.equal(2);
    let players = await contract.getPlayers();
    for (let p of players) {
      console.log("ACCEPTED PLAYER: ", p.username);
    }
    expect(players.length).to.equal(2);
    let tokenId = await contract.tokenId();
    expect(tokenId.toNumber()).to.equal(2);
    let tokenURI = await contract.tokenURI(0);
    console.log(tokenURI);
  });

  it("Should show a snac balance for owner", async () => {
    const snacBalance = await snacContract.balanceOf(owner.address);
    console.log("SNAC Balance:", snacBalance.toNumber());
    expect(snacBalance.toNumber()).to.be > 0;
  });

  it("Should allow owner to deposit and transfer snacs", async () => {
    let ownerSnacBalance = await snacContract.balanceOf(owner.address);
    console.log("Owner SNAC Balance:", ownerSnacBalance.toNumber());
    expect(ownerSnacBalance.toNumber()).to.be > 0;
    await snacContract.transfer(contract.address, 100);
    let contractBalance = await snacContract.balanceOf(contract.address);
    console.log("Contract SNAC Balance:", contractBalance.toNumber());
    // await contract.depositSnacs(100);
    await contract.rewardSnacs(bob.address, 10);
    let bobSnacBalance = await snacContract.balanceOf(bob.address);
    ownerSnacBalance = await snacContract.balanceOf(owner.address);
    contractBalance = await snacContract.balanceOf(contract.address);
    console.log("Bob SNAC Balance:", bobSnacBalance.toNumber());
    console.log("Owner SNAC Balance:", ownerSnacBalance.toNumber());
    console.log("Contract SNAC Balance:", contractBalance.toNumber());
    expect(bobSnacBalance.toNumber()).to.be > 0;
    expect(ownerSnacBalance.toNumber()).to.be < 26000;
  });

  it("Should create a bot, create a game, save it, and load it again.", async () => {
    await contract.requestPlayer("Owner", owner.address);
    const requests = await contract.getRequests();
    await contract.approvePlayer(0, true);
    await contract.createBot("Hippo", 1350);
    await contract.createGame();
    var game = await contract.loadGame();
    console.log("Game:", game);
    const moves = "I have some good moves."
    await contract.saveGame(moves);
    let loadedGame = await contract.loadGame();
    console.log("Loaded Game:", loadedGame);
    console.log("Moves:", loadedGame.moves);
  });
  
});
