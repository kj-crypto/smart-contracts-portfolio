# :open_file_folder: Portfolio of smart contracts :pushpin:

This repository is a portfolio of different smart contract implementations, like ERC token standards and others smart contract applications based on open source tutorials.

## :gem: Tokens
This section focuses on implementation, from scratch, of different token standards, including fungible and non-fungible tokens like ERC20 and ERC721.

Directory `tokens/contracts/tokens` contains following contracts:
- [BasicErc20](tokens/contracts/tokens/BasicErc20.sol) token is an ERC20 token with minimal functionality of the standard
- [MetaErc20](tokens/contracts/tokens/MetaErc20.sol) token is an ERC20 token with additional metadata like: `name`, `symbol` and `decimals` fields
- [MintableErc20](tokens/contracts/tokens/MintableErc20.sol) token is an ERC20 token that total supply can by changed by minting or burning the tokens
- [BasicErc223](tokens/contracts/tokens/BasicErc223.sol) is a token based of [EIP223](https://github.com/ethereum/EIPs/issues/223) which protects against accidentally token burning by sending to wrong contract address
- [BasicErc677](tokens/contracts/tokens/BasicErc677.sol) applies `transferAndCall` mechanism based on [EIP677](https://github.com/ethereum/EIPs/issues/677), which reduces service usage `ERC20` token payment from 2 transaction, `approve` and `transferFrom`, to single one. More detailed explanation can be found in article  [Ethereum smart service payment with tokens](https://medium.com/@jgm.orinoco/ethereum-smart-service-payment-with-tokens-60894a79f75c)
- [Erc721](tokens/contracts/tokens/Erc721.sol) is a NTF token based on [EIP721](https://eips.ethereum.org/EIPS/eip-721) standard

## :chains:  freeCodeCamp/Chainlink tutorial
In `free-code-camp` directory there are projects based on tutorial https://www.youtube.com/watch?v=M576WGiDBdQ. There are a following projects:
- `web3.py` located in `free-code-camp/web3` catalogue which is focused on deploying and testing [SimpleStorage](free-code-camp/web3/SimpleStorage.sol) by using [web3.py](https://web3py.readthedocs.io/en/stable/) library
- [FoundMe](free-code-camp/contracts/fund_me/FundMe.sol) is simple funding contract using chainlink price feed
- [Lottery](free-code-camp/contracts/lottery/Lottery.sol) is simple lottery using chainlink VRF to find random winner
- proxy pattern contracts, located in `free-code-camp/contracts/proxy`, relayed on Openzeppelin `TransparentUpgradeableProxy` support
- [TokenFarm](free-code-camp/contracts/stake-yield/TokenFarm.sol) is simple yield farming based on 3 ERC20 tokens used for staking and one ERC20 token used as a reward token returns when unstake is call

## 🏗 Scaffold-ETH challenges
This section is based on [scaffold eth challenges](https://github.com/scaffold-eth/scaffold-eth-challenges/tree/master). There are implemented following ones:

- in `scaffold-challenges/contracts/staking` are contracts for decentralized staking challenge
- in `scaffold-challenges/contracts/vendor_token` are contracts for token vendor challenge
- in `scaffold-challenges/contracts/dex` there is simple DEX  based on product AMM
- [RandomGenerator](scaffold-challenges/contracts/randomness/RandomGenerator.sol) is a contract of random number generator based on [commit reveal](https://github.com/scaffold-eth/scaffold-eth-examples/tree/commit-reveal-with-frontend) pattern. In case of trouble shoot in test suite, run tests again
- [Multisig](scaffold-challenges/contracts/multisig/Multisig.sol) is a contract implementing multi signature wallet N of M, which requires N signers from M allowed signer to transfer Eth to destination address

## :left_right_arrow: Proxy contracts
This section covers implementation of proxy contract, which allows for future contract upgrades of bug fixing. Code, located in `proxy-pattern/contracts` relays on following article [Upgradeable proxy contract from scratch](https://medium.com/coinmonks/upgradeable-proxy-contract-from-scratch-3e5f7ad0b741)
## :hammer_and_wrench: How to run

- install `ganache-cli` version `6.12.2`
- install `brownie` version `1.18.1`
- choose project directory and run `brownie test` inside it
- :new: optional [blockscout](https://github.com/kj-crypto/blockscout-exlpore) explorer can by used to view what happen on chain, it's enough to up and run explorer and set `BLOCKSCOUT_PUBLISH=true` env e.g in `.env` file


### :scroll: TODO List
- implement `ERC777` standard
- implement `ERC1155` standard
- implement `ERC721Enumerable` interface
