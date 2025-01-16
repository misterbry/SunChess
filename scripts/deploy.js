const hre = require("hardhat");

async function main() {

  // Deploy SNAC contract
  const Snac = await hre.ethers.getContractFactory("SunsetNeighborhoodAltCoin");
  const gasLimitSnac = await hre.ethers.provider.estimateGas(Snac.getDeployTransaction());
  const gasPriceSnac = await hre.ethers.provider.getGasPrice();
  const snac = await Snac.deploy();
  await snac.deployed();
  console.log("SNAC deployed to: ", snac.address);
 
  // Deploy SunChess contract
  const SunChess = await hre.ethers.getContractFactory("SunChess");
  const gasLimit = await hre.ethers.provider.estimateGas(SunChess.getDeployTransaction("OBCoin", "OBC", snac.address));
  const gasPrice = await hre.ethers.provider.getGasPrice();
  const tx = {
    gasLimit: gasLimit,
    gasPrice: gasPrice
  }
  const sunChess = await SunChess.deploy("OBCoin", "OBC", snac.address, tx);
  await sunChess.deployed();
  console.log("SunChess deployed to: ", sunChess.address);
}  

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
