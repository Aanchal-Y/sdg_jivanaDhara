const hre = require("hardhat");

async function main() {
  const ProofStore = await hre.ethers.getContractFactory("ProofStore");
  const proof = await ProofStore.deploy();
  await proof.deployed();
  console.log("ProofStore deployed to:", proof.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
