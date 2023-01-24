from scripts.helpful_scripts import get_account, from_gwei
from brownie import config, network, interface
from scripts.get_weth import get_weth
import time
from web3 import Web3
amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    # ABI and Address of Pool.sol from AAVE
    pool = get_pool()
    print(pool)

    # Approve sending our ERC20 tokens
    approve_erc20(amount, pool.address, erc20_address, account)

    # deposit
    print("Depositing....")
    tx = pool.supply(erc20_address, amount, account.address, 0, {
                     "from": account, "gas_price": 110000, "gas_limit": 1200000, "allow_revert": True})
    tx.wait(1)
    print("deposited!")
    # how much...?
    borrowable_usd, total_debt = get_borrowable_data(pool, account.address)
    # DAI in terms of eth
    dai_usd_price = get_asset_price(
        config["networks"][network.show_active()]["dai_usd_price_feed"])

    amount_dai_to_borrow = (1/dai_usd_price)*(borrowable_usd*0.95)
    print(f"We are going to borrow {int(amount_dai_to_borrow)}")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = pool.borrow(
        dai_address, Web3.toWei(amount_dai_to_borrow, "ether"), 1, 0, account.address, {"from": account, "gas_price": 110000, "gas_limit": 1200000, "allow_revert": True})
    print("Borrowed DAI (LOL)")
    get_borrowable_data(pool, account)
    repay_all(Web3.toWei(amount_dai_to_borrow), pool, account)
    print("You just deposited, borrowed, and Repaid with AAVE Brownie and ChainLink")


def repay_all(amount, pool, account):
    approve_erc20(Web3.toWei(amount, "ether"), pool,
                  config["networks"][network.show_active()]["dai_token"], account)

    repay_tx = pool.repay(config["networks"][network.show_active()]["dai_token"], amount, 1, account.address, {
                          "from": account, "gas_price": 110000, "gas_limit": 1200000, "allow_revert": True})

    repay_tx.wait(1)
    print("Repaid!!")


def get_asset_price(price_feed_address):
    # ABI
    # Address
    dai_usd_price_feed = interface.IAggregatorV3(price_feed_address)
    (
        roundId,
        answer,
        startedAt,
        updatedAt,
        answeredInRound
    ) = dai_usd_price_feed.latestRoundData()
    answer = from_gwei(answer)
    print(f"DAI USD price is {answer}")
    return float(answer)


def get_borrowable_data(pool, account):
    (total_collateral_eth, total_debt_eth, available_borrow_eth, current_liquidation_ratio,
     ltv, health_factor) = pool.getUserAccountData(account)
    total_collateral_eth = from_gwei(total_collateral_eth)
    total_debt_eth = from_gwei(total_debt_eth)
    available_borrow_eth = from_gwei(available_borrow_eth)
    print(f"you have total collateral eth worth {total_collateral_eth}")
    print(f"you have total debt eth worth {total_debt_eth}")
    print(f"you have available borrow eth worth {available_borrow_eth}")
    return (float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spenderAddress, erc20_token, account):
    print("Approving ERC20 token")
    erc20 = interface.IERC20(erc20_token)
    tx = erc20.approve(spenderAddress, amount, {
                       "from": account, "gas_price": 1000000000})
    tx.wait(1)
    print("Approved!")

    # ABI
    # Address


def get_pool():
    # Address- check
    pool_addresses_provider = interface.IPoolAddressesProvider(
        config["networks"][network.show_active()]["pool_address_provider"])
    pool_address = pool_addresses_provider.getPool()

    # ABI- check
    pool = interface.IPool(pool_address)
    return pool
