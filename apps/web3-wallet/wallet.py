from eth_account import Account

Account.enable_unaudited_hdwallet_features()

def get_wallet():
    acct, mnemonic = Account.create_with_mnemonic()
    return acct, mnemonic