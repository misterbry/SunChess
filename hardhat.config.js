require("dotenv").config();
require("@nomiclabs/hardhat-ethers");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
	enabled: true,
	runs: 200
      }
    }
  },
  networks: {
    polygon: {
      url: process.env.POLYGON_NODE,
      accounts: [process.env.PRIVATE_KEY]
    },
    amoy: {
      url: process.env.AMOY_NODE,
      accounts: [process.env.PRIVATE_KEY],
      // gasLimit: 4797582,
      // gasPrice: 50000000000
    },
    hardhat: {
      accounts: {
	count: 10
      }
    }
  }
};
