from brownie import network, accounts, config
FORKED_LOCAL_ENVIRONMENT = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    # .yaml works like a dictionary :)
    # accounts[0]
    # accounts.add("env")
    # accounts.load("ID")
    if index:
        return accounts[index]

    if id:
        return accounts.load(id)

    if (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENT):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


def from_gwei(amount):
    return amount/100000000
