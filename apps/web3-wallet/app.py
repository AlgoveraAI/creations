import gradio as gr
from ocean_lib.config import Config
from ocean_lib.models.btoken import BToken #BToken is ERC20
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.web3_internal.wallet import Wallet
from ocean_lib.web3_internal.currency import from_wei # wei is the smallest denomination of ether e.g. like cents
# from ocean_lib.web3_internal.currency import pretty_ether_and_wei
from wallet import get_wallet

config = Config('config.ini')
ocean = Ocean(config)

def wallet(private_key):
    
    if private_key:
        mnemonic = None
    else:
        account, mnemonic = get_wallet()

        private_key = account.key.hex()

    wallet = Wallet(ocean.web3, private_key, transaction_timeout=20, block_confirmations=config.block_confirmations)
    address = wallet.address

    OCEAN_token = BToken(ocean.web3, ocean.OCEAN_address)

    eth_balance = from_wei(ocean.web3.eth.get_balance(address))
    ocean_balance = from_wei(OCEAN_token.balanceOf(address))

    return address, private_key, mnemonic, eth_balance, ocean_balance

# def wallet(private_key, did):
#     wallet = Wallet(ocean.web3, private_key, transaction_timeout=20, block_confirmations=config.block_confirmations)
#     address = wallet.address
#     OCEAN_token = BToken(ocean.web3, ocean.OCEAN_address)

#     eth_balance = from_wei(ocean.web3.eth.get_balance(wallet.address))
#     ocean_balance = from_wei(OCEAN_token.balanceOf(wallet.address))

#     asset = ocean.assets.resolve(did)

#     ALG_ddo = ocean.assets.resolve(did)
#     alg_token = ocean.get_data_token(ALG_ddo.data_token_address)

#     alg_token_balance = pretty_ether_and_wei(alg_token.balanceOf(wallet.address))

#     return address, eth_balance, ocean_balance, alg_token_balance

description = (
    "This demo shows the balance of tokens in your Web3 wallet. If you do not have a Web3 wallet, leave the input field empty when running and the app will create a wallet for you. " 
    "A wallet consists of a public and private key. You can think of the public key like your email address and the private key like your password. "
    "The public key can be easily determined from the private key, but not vice versa. "
    "The private key is output in the form of both a hexadecimal number and the corresponding mnemonic phrase, which is easier to remember. " 
    "If you want to continue to use the same wallet in future, you should store the private key (and/or the mnemonic phrase, which can be used to recover the private key). " 
    "Then enter the private key to the input field when running the app. " 
    "Do not give your private key to anyone ever. In fact, it is bad practice to store your private key on your PC for wallets that contain tokens with real value. "
    "However, we are using test tokens on the Ethereum test network (Rinkeby) where the tokens have no real value. "
    "Initially, your wallet should have no ETH and OCEAN tokens in it. You can then request ETH and OCEAN test tokens by entering your public address into faucets (follow the links at the bottom of the page). "
    "Then wait about 15 seconds and re-run the app for the same private key. " 
    "This demo uses the Ocean Protocol Python library in the backend. For more information on the advantages of combinining Ocean and HuggingFace, check out the blog post link below. "
    ""
)

# description = (
#     "This demo shows the balance of algorithm tokens, as well as ETH and OCEAN, in your Web3 wallet (for a given private key). The algorithm tokens will be used to run Algovera apps on HF spaces in future. " 
#     "Currently, you need to export your private key from a MetaMask wallet (we plan to randomly generate a private key in the app and bypass MetaMask in future). "
#     "For a guide on how to install MetaMask (an extension in your browser), check the link at the bottom of the page. "
#     "We highly recommend doing this with a wallet that has no real tokens in it. We use a test network (Rinkeby) where the tokens have no real value. "
#     "After an initial setup, your wallet should have no tokens. You can request ETH and OCEAN test tokens from faucets at the links at the bottom of the page. "
#     "To buy an algorithm token (using the OCEAN and ETH), you can search for algorithms on the Ocean marketplace (see link at bottom). Make sure to use algorithms that are on the Rinkeby test network (you need to select Rinkeby from the dropdown menu). "
#     "We have provided a link to our DCGAN model on the test network at the bottom. If you can't see it you are not on the test network. "
#     "After you buy an algorithm token, you need to locate the DID in the metadata on the marketplace. Then enter it into the input textbox. "
#     "Later we will add HF Spaces apps to search algorithms and buy algorithm tokens, which you can use to run demos of the algorithms. "
#     "This demo uses the Ocean Python library in the backend (see link below)."
# )

article = (
    "<p style='text-align: center'>"
    "<a href='https://faucet.rinkeby.io/' target='_blank'>1. ETH faucet</a> | "
    "<a href='https://faucet.rinkeby.oceanprotocol.com/' target='_blank'>2. OCEAN faucet | </a>"
    "<a href='https://docs.algovera.ai/blog/2022/01/04/Using%20the%20Ocean%20Marketplace%20with%20HuggingFace%20Apps,%20Algorithms%20and%20Datasets' target='_blank'>3. Blog about Ocean Protocol on HuggingFace</a> "
    "</p>"
)


interface = gr.Interface(
    wallet,
    [
        gr.inputs.Textbox(label="Private Key"),
    ],
    [
        #gr.outputs.Textbox(label="Public Key"),
        #gr.outputs.Textbox(label="Algorithm token balance"),
        gr.outputs.Textbox(label="Public Address"),
        gr.outputs.Textbox(label="Private Key"),
        gr.outputs.Textbox(label="Recovery Passphrase"),
        gr.outputs.Textbox(label="ETH balance"),
        gr.outputs.Textbox(label="OCEAN balance"),
    ],
    title="Web3 Wallet",
    description=description,
    article=article,
    theme="huggingface",
)

interface.launch()