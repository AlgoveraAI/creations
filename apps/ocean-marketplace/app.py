import gradio as gr
from ocean_lib.config import Config
# from ocean_lib.models.btoken import BToken #BToken is ERC20
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.web3_internal.wallet import Wallet
# from ocean_lib.web3_internal.currency import from_wei # wei is the smallest denomination of ether e.g. like cents
from ocean_lib.web3_internal.currency import pretty_ether_and_wei
from ocean_lib.web3_internal.constants import ZERO_ADDRESS
# from wallet import get_wallet
from ocean_lib.common.agreements.service_types import ServiceTypes
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


config = Config('config.ini')
ocean = Ocean(config)

def search(term="", did_in="", address="", buy_top_result=False):

    if address:
        wallet = Wallet(ocean.web3, private_key=address, transaction_timeout=20, block_confirmations=0)
    
    results = None
    dids = None
    data=None
    if term:
        assets = ocean.assets.search(term)

        results = []
        datas = []
        balances = []
        dids = []
        for i in range(len(assets)):

            name = assets[i].values['_source']['service'][0]['attributes']['main']['name']
            type_ = assets[i].values['_source']['service'][0]['attributes']['main']['type'].upper()
            symbol = assets[i].values['_source']['dataTokenInfo']['symbol']
            data_token_address = assets[i].values['_source']['dataTokenInfo']['address']
            description = assets[i].values['_source']['service'][0]['attributes']['additionalInformation']['description']
            author = assets[i].values['_source']['service'][0]['attributes']['main']['author']
            did = assets[i].values['_source']['id']
            dids.append(did)
            chain = assets[i].values['_source']['service'][1]['serviceEndpoint']
            
            if chain != 'https://provider.rinkeby.oceanprotocol.com':
                continue
            
            if address:
                data_token = ocean.get_data_token(data_token_address)
                token_address = data_token.address
                balances.append(pretty_ether_and_wei(data_token.balanceOf(wallet.address)))
            else:
                balances.append(0)
            
            img = Image.open('algovera-tile.png')

            fig = plt.figure(figsize=(5,5))
            plt.axis("off")
            plt.imshow(img)
            plt.text(20, 100, name[:22], size=20)
            plt.text(20, 60, symbol)
            plt.text(400, 40, type_)
            plt.text(20, 140, author, size=12)
            plt.text(20, 200, description[:50])
            fig.tight_layout()
            fig.canvas.draw()
            data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            datas.append(data.reshape(fig.canvas.get_width_height()[::-1] + (3,)))
            plt.close()
            
            results.append([dids[-1], datas[-1], balances[-1]])

    print('%%%%%%%%%%', type(did_in))
    if did_in:
        results = []
        dids = []
        
        asset = ocean.assets.resolve(did_in)
        
        name = asset.as_dictionary()['service'][0]['attributes']['main']['name']
        type_ = asset.as_dictionary()['service'][0]['attributes']['main']['type'].upper()
        symbol = asset.as_dictionary()['dataTokenInfo']['symbol']
        description = asset.as_dictionary()['service'][0]['attributes']['additionalInformation']['description']
        author = asset.as_dictionary()['service'][0]['attributes']['main']['author']
        dids.append(did_in)
        chain = asset.as_dictionary()['service'][1]['serviceEndpoint']
        
        if chain != 'https://provider.rinkeby.oceanprotocol.com':
            pass
        
        if address:
            data_token = ocean.get_data_token(asset.data_token_address)
            token_address = data_token.address
            balances.append(pretty_ether_and_wei(data_token.balanceOf(wallet.address)))
        else:
            balances.append(0)
        
        
        
        img = Image.open('algovera-tile.png')

        fig = plt.figure(figsize=(5,5))
        plt.axis("off")
        plt.imshow(img)
        plt.text(20, 100, name[:22], size=20)
        plt.text(20, 60, symbol)
        plt.text(400, 40, type_)
        plt.text(20, 140, author, size=12)
        plt.text(20, 200, description[:50])
        fig.tight_layout()
        fig.canvas.draw()
        data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        datas.append(data.reshape(fig.canvas.get_width_height()[::-1] + (3,)))
        plt.close()
        
        results.append([dids[-1], datas[-1], balances[-1]])
        
    if buy_top_result:
        asset = ocean.assets.resolve(dids[0])
        service_type = asset.as_dictionary()['service'][1]['type']
        compute_service = asset.get_service(service_type)
        
        dataset_order_requirements = ocean.assets.order(
            asset.did, wallet.address, service_type=compute_service.type
        )
        DATA_order_tx_id = ocean.assets.pay_for_service(
                ocean.web3,
                dataset_order_requirements.amount,
                dataset_order_requirements.data_token_address,
                asset.did,
                compute_service.index,
                ZERO_ADDRESS,
                wallet,
                dataset_order_requirements.computeAddress,
            )

        if address:
            data_token = ocean.get_data_token(asset.data_token_address)
            token_address = data_token.address
            balance = pretty_ether_and_wei(data_token.balanceOf(wallet.address))
    
        results[0][2] = balance

    return results 

description = (
    "This app can be used to search datasets and algorithms on the Ocean Marketplace. Enter a search term in the text box and the first result will be displayed as an image tile with description. " 
)

article = (
    "<p style='text-align: center'>"
    "<a href='https://market.oceanprotocol.com/' target='_blank'>1. Ocean Marketplace</a> | "
    "<a href='https://docs.algovera.ai/blog/2022/01/04/Using%20the%20Ocean%20Marketplace%20with%20HuggingFace%20Apps,%20Algorithms%20and%20Datasets' target='_blank'>2. Blog about Ocean Protocol on HuggingFace</a> "
    "</p>"
)


interface = gr.Interface(
    search,
    [
        gr.inputs.Textbox(label="Search Datasets and Algorithms by name"),
        gr.inputs.Textbox(label="Search Datasets and Algorithms by DID"),
        gr.inputs.Textbox(label="Show Token Balance for Each (by Inputting Private Key)"),
        "checkbox"

    ],
    [
        gr.outputs.Carousel(["text", "image", "text"], label="Search Results"),
    ],
    title="Ocean Marketplace",
    description=description,
    article=article,
    theme="huggingface",
)

interface.launch()