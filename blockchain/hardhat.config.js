require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

const { ALCHEMY_API_URL, PRIVATE_KEY } = process.env;

module.exports = {
  solidity: "0.8.20",
  networks: {
    polygonMumbai: {
      url: ALCHEMY_API_URL,      // e.g. https://polygon-mumbai.g.alchemy.com/v2/KEY
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : []
    }
  }
};
